import asyncio
import contextlib
from collections.abc import Sequence
from contextlib import AbstractAsyncContextManager
from pathlib import PurePath

from result import Err, Ok, Result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.images.services import ImageService
from app.core.domain.manga.chapters.dto import ChapterCreateDTO
from app.core.domain.manga.chapters.repositories import ChapterRepository
from app.core.errors import EntityAlreadyExistsError, PermissionDeniedError
from app.core.storage import FileStorage, FileUpload
from app.db.models import (
    Group,
    Image,
    Manga,
    MangaBranch,
    MangaChapter,
    MangaPage,
    User,
)
from app.settings import AppSettings, ImagePaths, ImageSettings
from lib.db import DBContext
from lib.files import File


class ChapterPermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def can_create_chapter(self, user: User, branch: MangaBranch) -> bool:
        stmt = select(Group).where(Group.id == branch.group_id)
        group = (await self._session.scalars(stmt)).one()
        return group.created_by_id == user.id


class ChapterService:
    def __init__(  # noqa: PLR0913
        self,
        db_context: DBContext,
        image_storage: FileStorage,
        image_service: ImageService,
        permissions: ChapterPermissionService,
        repository: ChapterRepository,
        app_settings: AppSettings,
        image_settings: ImageSettings,
    ) -> None:
        self._db_context = db_context
        self._image_storage = image_storage
        self._image_service = image_service
        self._permissions = permissions
        self._repository = repository
        self._app_settings = app_settings
        self._image_settings = image_settings

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
        limiter = asyncio.Semaphore(self._app_settings.max_concurrent_uploads)
        async with contextlib.AsyncExitStack() as exit_stack:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self._upload_image(
                            branch=branch,
                            chapter=chapter,
                            number=number,
                            file=file,
                            exit_stack=exit_stack,
                            limiter=limiter,
                        ),
                    )
                    for number, file in enumerate(dto.pages, start=1)
                ]
            results = [task.result() for task in tasks]
            chapter.pages = [
                MangaPage(
                    images=list(images),
                    number=number,
                    chapter=chapter,
                )
                for number, images in enumerate(results, start=1)
            ]
            self._update_manga(manga=branch.manga, chapter=chapter)
            self._db_context.add(chapter)
            await self._db_context.flush()
        return Ok(chapter)

    async def _upload_image(  # noqa: PLR0913
        self,
        branch: MangaBranch,
        chapter: MangaChapter,
        number: int,
        file: File,
        exit_stack: contextlib.AsyncExitStack,
        limiter: AbstractAsyncContextManager[None],
    ) -> Sequence[Image]:
        upload = FileUpload(
            path=PurePath(
                f"{ImagePaths.chapter_images}/{branch.manga_id}/{chapter.id}/{number}{file.filename.suffix}",
            ),
            file=file,
        )

        async with limiter:
            return await exit_stack.enter_async_context(
                self._image_service.upload_src_set(
                    upload=upload,
                    src_set=self._image_settings.manga_page_src_set,
                ),
            )

    def _update_manga(self, manga: Manga, chapter: MangaChapter) -> None:
        manga.latest_chapter_id = chapter.id
        self._db_context.add(manga)
