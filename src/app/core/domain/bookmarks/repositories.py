from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga, MangaBookmark, User


class BookmarkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, manga: Manga, user: User) -> MangaBookmark | None:
        stmt = select(MangaBookmark).where(
            MangaBookmark.manga == manga,
            MangaBookmark.user == user,
        )
        return (await self._session.scalars(stmt)).one_or_none()
