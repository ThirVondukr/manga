import asyncio
import collections
import contextlib
import dataclasses
import itertools
import re
import tempfile
from collections.abc import AsyncIterator, Sequence
from io import BytesIO
from pathlib import Path, PurePath
from uuid import UUID
from zipfile import ZipFile

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.domain.chapters.services import ChapterService
from app.core.storage import FileStorage, FileUpload
from app.db.models import MangaBranch, MangaChapter, MangaPage, User
from app.settings import ImagePaths
from lib.files import File


@dataclasses.dataclass(kw_only=True, slots=True)
class PageMeta:
    filename: str

    title: str
    page: int
    chapter: int
    volume: int


@dataclasses.dataclass(kw_only=True, slots=True)
class ChapterMeta:
    chapter: int
    volume: int
    pages: Sequence[tuple[BytesIO, PageMeta]]


@dataclasses.dataclass(kw_only=True, slots=True)
class MangaFiles:
    title: str
    chapters: Sequence[ChapterMeta]


def parse_filename(name: str) -> PageMeta:
    title = re.search(r"(.*?)\s-", name).group(1)  # type: ignore[union-attr]
    page = re.search(r"p0*(\d+)", name).group(1)  # type: ignore[union-attr]
    chapter = re.search(r"c0*(\d+)", name).group(1)  # type: ignore[union-attr]
    volume = re.search(r"v0*(\d+)", name).group(1)  # type: ignore[union-attr]
    return PageMeta(
        filename=name,
        title=title,
        page=int(page),
        chapter=int(chapter),
        volume=int(volume),
    )


async def _upload_file(
    storage: FileStorage,
    storage_path: PurePath,
    file_path: PurePath,
) -> str:
    async with aiofiles.open(file_path, "rb") as f:
        buffer = BytesIO(await f.read())
        return await storage.upload(
            file=FileUpload(buffer=buffer, path=storage_path),
        )


async def collect_pages(
    chapter: MangaChapter,
    directory: Path,
    storage: FileStorage,
) -> list[MangaPage]:
    tasks = {}
    async with asyncio.TaskGroup() as tg:
        for file_path, page in zip(directory.iterdir(), itertools.count(1)):
            storage_path = PurePath(
                f"{ImagePaths.chapter_images}/{chapter.id}/{page}{file_path.suffix}",
            )
            tasks[page] = tg.create_task(
                _upload_file(
                    storage=storage,
                    storage_path=storage_path,
                    file_path=file_path,
                ),
            )

    return [
        MangaPage(chapter=chapter, number=page, image_path=path.result())
        for page, path in tasks.items()
    ]


async def _parse_file(path: Path) -> tuple[BytesIO, PageMeta]:
    async with aiofiles.open(path, "rb") as file:
        return BytesIO(await file.read()), parse_filename(path.name)


async def parse_files(path: Path) -> Sequence[tuple[BytesIO, PageMeta]]:
    tasks = [_parse_file(image_path) for image_path in path.iterdir()]
    return await asyncio.gather(*tasks)


@contextlib.asynccontextmanager
async def unpack(archive_path: Path) -> AsyncIterator[MangaFiles]:
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        ZipFile(archive_path) as zip_file,
    ):
        zip_file.extractall(path=temp_dir)

        pages = await parse_files(Path(temp_dir))
        chapters = collections.defaultdict(list)
        for buffer, page in pages:
            chapters[page.volume, page.chapter].append((buffer, page))

        yield MangaFiles(
            title=pages[0][1].title,
            chapters=[
                ChapterMeta(
                    volume=volume,
                    chapter=chapter,
                    pages=pages,
                )
                for (volume, chapter), pages in chapters.items()
            ],
        )


class ImportCBZCommand:
    def __init__(
        self,
        chapter_service: ChapterService,
        session: AsyncSession,
    ) -> None:
        self._chapter_service = chapter_service
        self._session = session

    async def execute(self, archive_path: Path) -> None:
        user = await self._session.get(
            User,
            UUID("018dec35-e637-734d-9c76-c8325ee4b914"),
        )
        if not user:
            raise ValueError
        branch = await self._session.get(
            MangaBranch,
            UUID("018e0315-fd41-701f-8bc9-615e1f42088e"),
        )
        if not branch:
            raise ValueError
        async with unpack(archive_path) as manga_files:
            for chapter in manga_files.chapters:
                dto = ChapterCreateDTO(
                    branch_id=branch.id,
                    title="",
                    number=[chapter.chapter],
                    volume=chapter.volume,
                    pages=[
                        File(
                            content_type="image/png",
                            size=buffer.getbuffer().nbytes,
                            buffer=buffer,
                            filename=PurePath(page.filename),
                        )
                        for buffer, page in chapter.pages
                    ],
                )
                await self._chapter_service.create(
                    dto=dto,
                    user=user,
                    branch=branch,
                )
