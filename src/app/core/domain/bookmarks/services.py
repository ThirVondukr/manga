from app.core.domain.bookmarks.repositories import BookmarkRepository
from app.db.models import Manga, MangaBookmark, User
from lib.db import DBContext


class BookmarkService:
    def __init__(
        self,
        db_context: DBContext,
        repository: BookmarkRepository,
    ) -> None:
        self._db_context = db_context
        self._repository = repository

    async def bookmark(self, manga: Manga, user: User) -> MangaBookmark:
        if bookmark := await self._repository.get(manga=manga, user=user):
            return bookmark

        bookmark = MangaBookmark(manga=manga, user=user)
        self._db_context.add(bookmark)
        await self._db_context.flush()
        return bookmark
