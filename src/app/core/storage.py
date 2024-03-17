import contextlib
import dataclasses
import mimetypes
from collections.abc import AsyncIterator, Collection, Sequence
from contextlib import AbstractAsyncContextManager
from pathlib import PurePath
from typing import Protocol, final, runtime_checkable

import aioboto3
from types_aiobotocore_s3 import S3Client

from app.settings import S3Settings
from lib.files import FileProtocol


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
    file: FileProtocol
    path: PurePath


@runtime_checkable
class FileStorage(Protocol):

    async def upload_file(self, file: FileUpload) -> str: ...

    async def url(self, path: str) -> str: ...

    def upload_contexts(
        self,
        files: Sequence[FileUpload],
    ) -> AbstractAsyncContextManager[tuple[str, ...]]: ...

    def upload_context(
        self,
        file: FileUpload,
    ) -> AbstractAsyncContextManager[str]: ...

    async def delete(self, keys: Collection[str]) -> None: ...


@final
class S3FileStorage(FileStorage):
    def __init__(self, client: S3Client, settings: S3Settings) -> None:
        self._client = client
        self._settings = settings

    async def upload_file(self, file: FileUpload) -> str:
        path = file.path.as_posix()
        mimetype, _ = mimetypes.guess_type(url=file.path.name)
        upload_id = (
            await self._client.create_multipart_upload(
                Bucket=self._settings.bucket,
                Key=path,
                ContentType=mimetype or "binary/octet-stream",
            )
        )["UploadId"]
        e_tags = []
        part_number = 1
        while chunk := await file.file.read(
            size=self._settings.multipart_upload_chunk_size,
        ):
            part_upload_response = await self._client.upload_part(
                Bucket=self._settings.bucket,
                Key=path,
                Body=chunk,
                PartNumber=part_number,
                UploadId=upload_id,
            )
            e_tags.append(
                (part_number, part_upload_response["ETag"].replace('"', "")),
            )
            part_number += 1

        response = await self._client.complete_multipart_upload(
            Bucket=self._settings.bucket,
            Key=path,
            UploadId=upload_id,
            MultipartUpload={
                "Parts": [
                    {"PartNumber": part_number, "ETag": e_tag}
                    for part_number, e_tag in e_tags
                ],
            },
        )
        return response["Key"]

    async def url(self, path: str) -> str:
        return f"{self._settings.public_url.removesuffix('/')}/{self._settings.bucket}/{path.removesuffix('/')}"

    @contextlib.asynccontextmanager
    async def upload_contexts(
        self,
        files: Sequence[FileUpload],
    ) -> AsyncIterator[tuple[str, ...]]:
        uploaded = set()
        try:
            for file in files:
                path_str = await self.upload_file(file=file)
                uploaded.add(path_str)
            yield tuple(f.path.as_posix() for f in files)
        except:
            await self.delete(uploaded)
            raise

    @contextlib.asynccontextmanager
    async def upload_context(
        self,
        file: FileUpload,
    ) -> AsyncIterator[str]:
        path_str = await self.upload_file(file=file)
        try:
            yield path_str
        except:
            await self.delete(path_str)
            raise

    async def delete(self, keys: Collection[str]) -> None:
        if isinstance(keys, str):
            keys = [keys]

        await self._client.delete_objects(
            Bucket=self._settings.bucket,
            Delete={"Objects": [{"Key": path} for path in keys]},
        )
