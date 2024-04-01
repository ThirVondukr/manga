import contextlib
import sys
from collections.abc import AsyncIterator, Sequence
from io import BytesIO
from pathlib import PurePath

import PIL.Image

from app.core.storage import FileStorage, FileUpload
from app.db.models import Image
from app.settings import ImageSettings
from lib.db import DBContext
from lib.files import AsyncBytesIO


def _make_thumbnail(
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
    async def upload_src_set(
        self,
        upload: FileUpload,
        src_set: Sequence[int] | None = None,
    ) -> AsyncIterator[Sequence[Image]]:
        io = BytesIO(await upload.file.read())
        await upload.file.seek(0)
        original = PIL.Image.open(io)

        images = []
        async with contextlib.AsyncExitStack() as exit_stack:
            path = await exit_stack.enter_async_context(
                self._storage.upload_context(upload),
            )
            image_record = Image(
                path=PurePath(path),
                width=original.width,
                height=original.height,
            )
            images.append(image_record)
            src_set = (
                src_set
                if src_set is not None
                else self._settings.default_src_set
            )
            for width in src_set:
                if width >= original.width:
                    continue

                thumbnail_io, thumbnail = _make_thumbnail(
                    image=original,
                    width=width,
                    image_format=self._settings.thumbnail_image_format,
                    quality=self._settings.thumbnail_quality,
                )
                thumbnail_upload = FileUpload(
                    file=AsyncBytesIO(buffer=thumbnail_io),
                    path=upload.path.with_stem(
                        f"{upload.path.stem}-{width}w",
                    ).with_suffix(f".{self._settings.thumbnail_image_format}"),
                )
                path = await exit_stack.enter_async_context(
                    self._storage.upload_context(file=thumbnail_upload),
                )

                image_record = Image(
                    path=PurePath(path),
                    width=thumbnail.width,
                    height=thumbnail.height,
                )
                images.append(image_record)
            self._db_context.add_all(images)
            yield images
