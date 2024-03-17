import abc
import dataclasses
from collections.abc import Sequence
from io import BytesIO
from pathlib import PurePath
from typing import Protocol, assert_never

from result import Err, Ok, Result
from starlette.datastructures import UploadFile


class FileProtocol(Protocol):
    @property
    def size(self) -> int: ...

    async def read(self, size: int = -1) -> bytes: ...

    async def seek(self, offset: int) -> None: ...


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class File:
    filename: PurePath
    content_type: str
    size: int

    @abc.abstractmethod
    async def read(self, size: int = -1) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    async def seek(self, offset: int) -> None:
        raise NotImplementedError


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class StarletteFile(File):
    _file: UploadFile
    size: int

    async def read(self, size: int = -1) -> bytes:
        return await self._file.read(size)

    async def seek(self, offset: int) -> None:
        await self._file.seek(offset)


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class InMemoryFile(File):
    _buffer: BytesIO

    async def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    async def seek(self, offset: int) -> None:
        self._buffer.seek(offset)


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class AsyncBytesIO:
    buffer: BytesIO

    @property
    def size(self) -> int:
        return self.buffer.getbuffer().nbytes  # pragma: no cover

    async def read(self, size: int = -1) -> bytes:  # pragma: no cover
        return self.buffer.read(size)

    async def seek(self, offset: int) -> None:  # pragma: no cover
        self.buffer.seek(offset)


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
        while chunk := await file.read(self._chunk_size):
            total_size += len(chunk)
            if total_size > self._max_size:  # pragma: no cover
                return Err(
                    FileReadError(
                        f"Upload size of {total_size} exceeds max size of {self._max_size}",
                    ),
                )

        await file.seek(0)
        match file:
            case UploadFile():
                return Ok(
                    StarletteFile(
                        _file=file,
                        size=file.size,
                        content_type=file.content_type,
                        filename=PurePath(file.filename),
                    ),
                )
        assert_never(file)  # pragma: no cover
