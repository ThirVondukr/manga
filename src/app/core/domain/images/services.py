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
    width: int | None,
) -> tuple[BytesIO, PIL.Image.Image]:
    io = BytesIO()
    thumbnail = image.copy()
    if width is not None:
        thumbnail.thumbnail(size=(width, sys.maxsize))
    thumbnail.save(io, format=image.format)
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
    async def upload_image_with_preview(
        self,
        upload: FileUpload,
        max_width: int,
    ) -> AsyncIterator[tuple[Image, Image]]:
        io = BytesIO(await upload.file.read())
        await upload.file.seek(0)
        thumbnail = PIL.Image.open(io)
        image_width, image_height = thumbnail.width, thumbnail.height

        thumbnail.thumbnail(size=(max_width, sys.maxsize))  # Only scale width
        thumbnail_io = BytesIO()
        thumbnail.save(
            thumbnail_io,
            format=thumbnail.format,
        )

        thumbnail_io.seek(0)

        async with (
            self._storage.upload_context(file=upload) as main,
            self._storage.upload_context(
                file=FileUpload(
                    path=upload.path.with_stem(f"{upload.path.stem}-preview"),
                    file=AsyncBytesIO(buffer=thumbnail_io),
                ),
            ) as preview,
        ):
            main_image = Image(
                path=PurePath(main),
                width=image_width,
                height=image_height,
            )
            preview_image = Image(
                path=PurePath(preview),
                width=thumbnail.width,
                height=thumbnail.height,
            )
            self._db_context.add(main_image)
            self._db_context.add(preview_image)
            yield main_image, preview_image

    @contextlib.asynccontextmanager
    async def upload_src_set(
        self,
        upload: FileUpload,
    ) -> AsyncIterator[Sequence[Image]]:
        io = BytesIO(await upload.file.read())
        await upload.file.seek(0)
        image = PIL.Image.open(io)

        exit_stack = contextlib.AsyncExitStack()
        images = []
        async with exit_stack:
            thumbnail_io, thumbnail = _make_thumbnail(image=image, width=None)
            path = await exit_stack.enter_async_context(
                self._storage.upload_context(file=upload),
            )
            image_record = Image(
                path=PurePath(path),
                width=thumbnail.width,
                height=thumbnail.height,
            )
            images.append(image_record)

            for width in self._settings.src_set:
                if width >= image.width:
                    continue

                thumbnail_io, thumbnail = _make_thumbnail(
                    image=image,
                    width=width,
                )
                thumbnail_upload = FileUpload(
                    file=AsyncBytesIO(buffer=thumbnail_io),
                    path=upload.path.with_stem(f"{upload.path.stem}-{width}w"),
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
