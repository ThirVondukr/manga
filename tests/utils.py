import contextlib
import uuid
from collections.abc import AsyncIterator, Collection
from io import BytesIO
from pathlib import PurePath
from typing import final

import PIL.Image

from app.core.storage import FileStorage, FileUpload
from lib.files import File, InMemoryFile


def casefold(string: str) -> str:
    return string.replace(" ", "").casefold()


def casefold_obj(obj: object) -> object:
    return casefold(obj) if isinstance(obj, str) else obj


def create_dummy_image() -> BytesIO:
    image = PIL.Image.new("RGB", (32, 32))
    io = BytesIO()
    image.save(io, format="png")
    io.seek(0)
    return io


def create_dummy_image_file() -> File:
    buffer = create_dummy_image()
    return InMemoryFile(
        _buffer=buffer,
        content_type="image/png",
        size=buffer.getbuffer().nbytes,
        filename=PurePath(f"{uuid.uuid4()}.png"),
    )


@final
class TestFileStorage(FileStorage):
    __test__ = False

    def __init__(self) -> None:
        self._prefix = str(uuid.uuid4())
        self.files: list[str] = []

    async def upload_file(
        self,
        file: FileUpload,
    ) -> str:
        path = file.path.as_posix()
        self.files.append(path)
        return path

    async def url(self, path: str) -> str:
        return f"{self._prefix}/{path}"

    @contextlib.asynccontextmanager
    async def upload_context(
        self,
        file: FileUpload,
    ) -> AsyncIterator[str]:
        yield await self.upload_file(file)

    async def delete(self, keys: Collection[str]) -> None:
        raise NotImplementedError
