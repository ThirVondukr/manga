import dataclasses
from collections.abc import Sequence
from io import BytesIO
from pathlib import PurePath

from result import Err, Ok, Result
from starlette.datastructures import UploadFile


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class File:
    buffer: BytesIO
    filename: PurePath
    content_type: str
    size: int


@dataclasses.dataclass
class FileReadError:
    pass


class FileReader:
    def __init__(self, max_size: int, chunk_size: int = 1024 * 1024) -> None:
        self._max_size = max_size
        self._chunk_size = chunk_size

    async def read(
        self,
        files: Sequence[UploadFile],
    ) -> Result[Sequence[File], FileReadError]:
        total_size = 0
        result = []
        for file in files:
            if not file.content_type or not file.filename or not file.size:
                return Err(FileReadError())

            buffer = BytesIO()
            while chunk := await file.read(self._chunk_size):
                total_size += len(chunk)
                if total_size > self._max_size:  # pragma: no cover
                    return Err(FileReadError())
                buffer.write(chunk)
            await file.seek(0)
            buffer.seek(0)

            result.append(
                File(
                    buffer=buffer,
                    size=file.size,
                    content_type=file.content_type,
                    filename=PurePath(file.filename),
                ),
            )

        return Ok(result)
