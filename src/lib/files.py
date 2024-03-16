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
    message: str


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
            file_result = await self.read_one(file=file)
            if isinstance(file_result, Err):
                return file_result

            total_size += file_result.ok_value.size
            if total_size > self._max_size:  # pragma: no cover
                return Err(
                    FileReadError(
                        f"Upload size of {total_size} exceeds max size of {self._max_size}",
                    ),
                )

            result.append(file_result.ok_value)

        return Ok(result)

    async def read_one(self, file: UploadFile) -> Result[File, FileReadError]:
        if not file.content_type or not file.filename or not file.size:
            return Err(FileReadError("Invalid file"))

        total_size = 0
        buffer = BytesIO()
        while chunk := await file.read(self._chunk_size):
            total_size += len(chunk)
            if total_size > self._max_size:  # pragma: no cover
                return Err(
                    FileReadError(
                        f"Upload size of {total_size} exceeds max size of {self._max_size}",
                    ),
                )
            buffer.write(chunk)
        await file.seek(0)
        buffer.seek(0)

        return Ok(
            File(
                buffer=buffer,
                size=file.size,
                content_type=file.content_type,
                filename=PurePath(file.filename),
            ),
        )
