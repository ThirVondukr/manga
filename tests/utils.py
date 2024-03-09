import contextlib
import uuid
from collections.abc import AsyncIterator, Sequence
from typing import final

from app.core.storage import FileUpload, ImageStorage


def casefold(string: str) -> str:
    return string.replace(" ", "").casefold()


def casefold_obj(obj: object) -> object:
    return casefold(obj) if isinstance(obj, str) else obj


@final
class TestImageStorage(ImageStorage):
    __test__ = False

    def __init__(self) -> None:
        self._prefix = str(uuid.uuid4())
        self.files: list[str] = []

    async def upload(
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
        files: Sequence[FileUpload],
    ) -> AsyncIterator[tuple[str, ...]]:
        to_upload = [f.path.as_posix() for f in files]
        yield tuple(f.path.as_posix() for f in files)
        self.files.extend(to_upload)
