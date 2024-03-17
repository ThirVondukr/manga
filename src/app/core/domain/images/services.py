import contextlib
import sys
from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import PurePath

import PIL.Image

from app.core.storage import FileStorage, FileUpload
from app.db.models import Image
from lib.db import DBContext
from lib.files import AsyncBytesIO


class ImageService:
    def __init__(self, storage: FileStorage, db_context: DBContext) -> None:
        self._storage = storage
        self._db_context = db_context

    @contextlib.asynccontextmanager
    async def upload_image_with_preview(
        self,
        upload: FileUpload,
        max_width: int,
    ) -> AsyncIterator[tuple[Image, Image]]:
        io = BytesIO(await upload.file.read())
        await upload.file.seek(0)
        thumbnail = PIL.Image.open(io)
        image_dimensions = thumbnail.size

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
                dimensions=image_dimensions,
            )
            preview_image = Image(
                path=PurePath(preview),
                dimensions=thumbnail.size,
            )
            self._db_context.add(main_image)
            self._db_context.add(preview_image)
            yield main_image, preview_image
