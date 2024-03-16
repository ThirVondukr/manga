from pathlib import PurePath

from result import Err, Ok, Result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.domain.chapters.repositories import ChapterRepository
from app.core.errors import EntityAlreadyExistsError, PermissionDeniedError
from app.core.storage import FileStorage, FileUpload
from app.db.models import (
    Group,
    Manga,
    MangaBranch,
    MangaChapter,
    MangaPage,
    User,
)
from app.settings import ImagePaths
from lib.db import DBContext


class ChapterPermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def can_create_chapter(self, user: User, branch: MangaBranch) -> bool:
        stmt = select(Group).where(Group.id == branch.group_id)
        group = (await self._session.scalars(stmt)).one()
        return group.created_by_id == user.id


class ChapterService:
    def __init__(
        self,
        db_context: DBContext,
        image_storage: FileStorage,
        permissions: ChapterPermissionService,
        repository: ChapterRepository,
    ) -> None:
        self._db_context = db_context
        self._image_storage = image_storage
        self._permissions = permissions
        self._repository = repository

    async def create(
        self,
        dto: ChapterCreateDTO,
        branch: MangaBranch,
        user: User,
    ) -> Result[MangaChapter, PermissionDeniedError | EntityAlreadyExistsError]:
        if not await self._permissions.can_create_chapter(
            user=user,
            branch=branch,
        ):
            return Err(PermissionDeniedError())

        if await self._repository.find_one(
            number=dto.number,
            branch_id=dto.branch_id,
        ):
            return Err(EntityAlreadyExistsError())

        chapter = MangaChapter(
            branch=branch,
            created_by=user,
            title=dto.title,
            volume=dto.volume,
            number=dto.number,
            pages=[],
        )
        files_to_upload = [
            FileUpload(
                path=PurePath(
                    f"{ImagePaths.chapter_images}/{branch.manga_id}/{chapter.id}/{number}{file.filename.suffix}",
                ),
                buffer=file.buffer,
            )
            for number, file in enumerate(dto.pages, start=1)
        ]
        async with self._image_storage.upload_context(files_to_upload) as files:
            chapter.pages = [
                MangaPage(image_path=path, number=number, chapter=chapter)
                for number, path in enumerate(files, start=1)
            ]
            self._update_manga(manga=branch.manga, chapter=chapter)
            self._db_context.add(chapter)
            await self._db_context.flush()
            return Ok(chapter)

    def _update_manga(self, manga: Manga, chapter: MangaChapter) -> None:
        manga.latest_chapter_id = chapter.id
        self._db_context.add(manga)
