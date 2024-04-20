from typing import Literal
from uuid import UUID

from sqlalchemy import Select, SQLColumnExpression, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.manga.manga.filters import (
    MangaBookmarkFilter,
    MangaBookmarkSortField,
    MangaSortField,
    Sort,
)
from app.core.domain.manga.manga.repositories import (
    filter_manga_stmt,
    sort_manga_stmt,
)
from app.db.models import User
from app.db.models.manga import Manga, MangaBookmark
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate
from lib.sort import SortDirection


def _sort_stmt(
    stmt: Select[tuple[MangaBookmark]],
    sort: Sort[MangaBookmarkSortField],
) -> Select[tuple[MangaBookmark]]:
    field: SQLColumnExpression[object]
    match sort.field:
        case (
            MangaBookmarkSortField.chapter_upload
            | MangaBookmarkSortField.created_at
            | MangaBookmarkSortField.title
        ):
            stmt = stmt.join(MangaBookmark.manga)
            return sort_manga_stmt(
                stmt,
                sort=Sort(
                    direction=sort.direction,
                    field=MangaSortField[sort.field.name],
                ),
            )
        case MangaBookmarkSortField.bookmark_added_at:
            field = MangaBookmark.created_at

    field = field if sort.direction is SortDirection.asc else field.desc()
    id_field = (
        MangaBookmark.manga_id
        if sort.direction is SortDirection.asc
        else MangaBookmark.manga_id.desc()
    )
    return stmt.order_by(field.nulls_last(), id_field)


def _filter_stmt(
    stmt: Select[tuple[MangaBookmark]],
    filter: MangaBookmarkFilter,
) -> Select[tuple[MangaBookmark]]:
    stmt = stmt.join(MangaBookmark.manga).group_by(
        MangaBookmark.manga_id,
        MangaBookmark.user_id,
    )
    if filter.manga:
        stmt = filter_manga_stmt(stmt=stmt, filter=filter.manga)
    if filter.statuses:
        stmt = stmt.where(MangaBookmark.status.in_(filter.statuses))
    return stmt


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
        sort: Sort[MangaBookmarkSortField],
        filter: MangaBookmarkFilter | None = None,
    ) -> PagePaginationResultDTO[MangaBookmark]:
        base_stmt = select(MangaBookmark).where(
            MangaBookmark.user_id == user_id,
        )
        stmt = base_stmt.join(MangaBookmark.manga)
        stmt = _sort_stmt(stmt=stmt, sort=sort)
        if filter is not None:
            stmt = _filter_stmt(stmt=stmt, filter=filter)
        return await page_paginate(
            stmt=stmt,
            session=self._session,
            pagination=pagination,
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
