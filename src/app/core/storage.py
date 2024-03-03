import contextlib
import mimetypes
from collections.abc import AsyncIterator
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


@runtime_checkable
class ImageStorage(Protocol):

    async def upload(self, path: PurePath, buffer: BytesIO) -> str: ...

    async def url(self, path: str) -> str: ...


@final
class S3ImageStorage(ImageStorage):
    def __init__(self, client: S3Client, settings: S3Settings) -> None:
        self._client = client
        self._settings = settings

    async def upload(
        self,
        path: PurePath,
        buffer: BytesIO,
    ) -> str:
        mimetype, _ = mimetypes.guess_type(url=path.name)
        await self._client.put_object(
            Body=buffer,
            Bucket=self._settings.bucket,
            Key=path.as_posix(),
            ContentType=mimetype or "binary/octet-stream",
        )
        return path.as_posix()

    async def url(self, path: str) -> str:
        return f"{self._settings.endpoint_url.removesuffix('/')}/{self._settings.bucket}/{path.removesuffix('/')}"
