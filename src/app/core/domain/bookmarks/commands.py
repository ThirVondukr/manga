from uuid import UUID

from result import Err, Ok, Result

from app.core.domain.bookmarks.dto import BookmarkMangaResultDTO
from app.core.domain.bookmarks.services import BookmarkService
from app.core.domain.manga.repositories import MangaRepository
from app.core.errors import NotFoundError
from app.db.models import Manga, User


class MangaBookmarkAddCommand:
    def __init__(
        self,
        manga_repository: MangaRepository,
        bookmark_service: BookmarkService,
    ) -> None:
        self._manga_repository = manga_repository
        self._bookmark_service = bookmark_service

    async def execute(
        self,
        user: User,
        manga_id: UUID,
    ) -> Result[BookmarkMangaResultDTO, NotFoundError]:
        if not (manga := await self._manga_repository.get(id=manga_id)):
            return Err(NotFoundError(entity_id=str(manga_id)))

        bookmark = await self._bookmark_service.add_bookmark(
            manga=manga,
            user=user,
        )
        return Ok(BookmarkMangaResultDTO(bookmark=bookmark, manga=manga))


class MangaBookmarkRemoveCommand:
    def __init__(
        self,
        manga_repository: MangaRepository,
        bookmark_service: BookmarkService,
    ) -> None:
        self._manga_repository = manga_repository
        self._bookmark_service = bookmark_service

    async def execute(
        self,
        user: User,
        manga_id: UUID,
    ) -> Result[Manga, NotFoundError]:
        if not (manga := await self._manga_repository.get(id=manga_id)):
            return Err(NotFoundError(entity_id=str(manga_id)))

        await self._bookmark_service.remove_bookmark(manga=manga, user=user)
        return Ok(manga)
