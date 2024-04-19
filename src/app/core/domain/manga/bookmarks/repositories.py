from typing import Literal
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.models.manga import Manga, MangaBookmark
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate


class BookmarkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, manga: Manga, user: User) -> MangaBookmark | None:
        stmt = select(MangaBookmark).where(
            MangaBookmark.manga == manga,
            MangaBookmark.user == user,
        )
        return (await self._session.scalars(stmt)).one_or_none()

    async def user_bookmarks(
        self,
        user_id: UUID,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[MangaBookmark]:
        base_stmt = select(MangaBookmark).where(
            MangaBookmark.user_id == user_id,
        )
        stmt = base_stmt.join(MangaBookmark.manga).order_by(
            Manga.title,
            Manga.id,
        )
        return await page_paginate(
            stmt=stmt,
            session=self._session,
            pagination=pagination,
            count_query=select(func.count()).select_from(base_stmt.subquery()),
        )

    async def delete(self, manga: Manga, user: User) -> None:
        stmt = delete(MangaBookmark).where(
            MangaBookmark.manga == manga,
            MangaBookmark.user == user,
        )
        await self._session.execute(stmt)

    async def change_bookmark_count(
        self,
        manga_id: UUID,
        delta: Literal[1, -1],
    ) -> None:
        stmt = (
            update(Manga)
            .values(bookmark_count=Manga.bookmark_count + delta)
            .where(Manga.id == manga_id)
        )
        await self._session.execute(stmt)
