import contextlib
import logging
import sys
from collections.abc import AsyncIterator, Sequence
from io import BytesIO
from pathlib import PurePath

import PIL.Image

from app.core.storage import FileStorage, FileUpload
from app.db.models import Image, ImageSet, ImageSetScaleTask
from app.settings import ImageSettings
from lib.db import DBContext
from lib.files import AsyncBytesIO
from lib.tasks import TaskStatus


def _make_thumbnail(  # pragma: no cover
    image: PIL.Image.Image,
    width: int,
    image_format: str,
    quality: int,
) -> tuple[BytesIO, PIL.Image.Image]:
    io = BytesIO()
    thumbnail = image.copy()
    thumbnail.thumbnail(size=(width, sys.maxsize))
    thumbnail.save(io, format=image_format, quality=quality)
    io.seek(0)
    return io, thumbnail


class ImageService:
    def __init__(
        self,
        storage: FileStorage,
        db_context: DBContext,
        settings: ImageSettings,
    ) -> None:
        self._storage = storage
        self._db_context = db_context
        self._settings = settings

    @contextlib.asynccontextmanager
    async def upload_image_set(
        self,
        upload: FileUpload,
        src_set: Sequence[int] | None = None,
    ) -> AsyncIterator[ImageSet]:
        io = BytesIO(await upload.file.read())
        await upload.file.seek(0)
        original = PIL.Image.open(io)

        async with contextlib.AsyncExitStack() as exit_stack:
            path = await exit_stack.enter_async_context(
                self._storage.upload_context(upload),
            )
            image_record = Image(
                path=PurePath(path),
                width=original.width,
                height=original.height,
            )
            src_set = tuple(
                (
                    src_set
                    if src_set is not None
                    else self._settings.default_src_set
                ),
            )
            image_set = ImageSet(original=image_record, images=[image_record])
            self._db_context.add(
                ImageSetScaleTask(
                    image_set=image_set,
                    widths=src_set,
                    status=TaskStatus.pending,
                ),
            )
            self._db_context.add(image_set)
            yield image_set

    async def scale_image_set(  # pragma: no cover
        self,
        image_set: ImageSet,
        task: ImageSetScaleTask,
        exit_stack: contextlib.AsyncExitStack,
    ) -> ImageSet:
        original_fileobj = await self._storage.download_file(
            path=image_set.original.path,
        )
        original = PIL.Image.open(original_fileobj.buffer)
        del original_fileobj
        for width in task.widths:
            if width >= image_set.original.width:
                continue

            logging.info(
                "Scaling image %s to %s",
                image_set.original.path,
                width,
            )
            thumbnail_io, thumbnail = _make_thumbnail(
                image=original,
                width=width,
                image_format=self._settings.thumbnail_image_format,
                quality=self._settings.thumbnail_quality,
            )
            thumbnail_upload = FileUpload(
                file=AsyncBytesIO(buffer=thumbnail_io),
                path=image_set.original.path.with_stem(
                    f"{image_set.original.path.stem}-{width}w",
                ).with_suffix(f".{self._settings.thumbnail_image_format}"),
            )
            del thumbnail_io
            path = await exit_stack.enter_async_context(
                self._storage.upload_context(file=thumbnail_upload),
            )
            image_record = Image(
                path=PurePath(path),
                width=thumbnail.width,
                height=thumbnail.height,
            )
            del thumbnail
            self._db_context.add(image_record)
            self._db_context.add(image_set)
        await self._db_context.flush()
        return image_set
