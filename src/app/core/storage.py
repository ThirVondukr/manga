import contextlib
import dataclasses
import mimetypes
from collections.abc import AsyncIterator, Sequence
from contextlib import AbstractAsyncContextManager
from io import BytesIO
from pathlib import PurePath
from typing import Protocol, final, runtime_checkable

import aioboto3
from types_aiobotocore_s3 import S3Client

from app.settings import S3Settings


@contextlib.asynccontextmanager
async def create_s3(settings: S3Settings) -> AsyncIterator[S3Client]:
    session = aioboto3.Session(
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
    )
    async with session.client(
        "s3",
        endpoint_url=settings.endpoint_url,
    ) as s3:
        yield s3


@dataclasses.dataclass
class FileUpload:
    buffer: BytesIO
    path: PurePath


@runtime_checkable
class ImageStorage(Protocol):

    async def upload(self, file: FileUpload) -> str: ...

    async def url(self, path: str) -> str: ...

    def upload_context(
        self,
        files: Sequence[FileUpload],
    ) -> AbstractAsyncContextManager[tuple[str, ...]]: ...


@final
class S3ImageStorage(ImageStorage):
    def __init__(self, client: S3Client, settings: S3Settings) -> None:
        self._client = client
        self._settings = settings

    async def upload(
        self,
        file: FileUpload,
    ) -> str:
        mimetype, _ = mimetypes.guess_type(url=file.path.name)
        await self._client.put_object(
            Body=file.buffer,
            Bucket=self._settings.bucket,
            Key=file.path.as_posix(),
            ContentType=mimetype or "binary/octet-stream",
        )
        return file.path.as_posix()

    async def url(self, path: str) -> str:
        return f"{self._settings.endpoint_url.removesuffix('/')}/{self._settings.bucket}/{path.removesuffix('/')}"

    @contextlib.asynccontextmanager
    async def upload_context(
        self,
        files: Sequence[FileUpload],
    ) -> AsyncIterator[tuple[str, ...]]:
        uploaded = set()
        try:
            for file in files:
                path_str = await self.upload(file=file)
                uploaded.add(path_str)
            yield tuple(f.path.as_posix() for f in files)
        except:
            await self._client.delete_objects(
                Bucket=self._settings.bucket,
                Delete={"Objects": [{"Key": path} for path in uploaded]},
            )
            raise
