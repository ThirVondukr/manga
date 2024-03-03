import uuid
from io import BytesIO
from pathlib import PurePath
from typing import final

from app.core.storage import ImageStorage


def casefold(string: str) -> str:
    return string.replace(" ", "").casefold()


@final
class TestImageStorage(ImageStorage):
    def __init__(self) -> None:
        self._prefix = str(uuid.uuid4())

    async def upload(
        self,
        path: PurePath,
        buffer: BytesIO,
    ) -> str:
        raise NotImplementedError

    async def url(self, path: str) -> str:
        return f"{self._prefix}/{path}"
