from collections.abc import Sequence
from typing import Any, TypeVar, assert_never
from uuid import UUID

from sqlalchemy import Select, SQLColumnExpression, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.orm.interfaces import ORMOption

from app.db.models.manga import AltTitle, Manga, MangaChapter, MangaTag
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate
from lib.sort import SortDirection

from .filters import MangaFilter, MangaFindFilter, MangaSortField, Sort

_T = TypeVar("_T", bound=tuple[Any, ...])


def sort_manga_stmt(stmt: Select[_T], sort: Sort[MangaSortField]) -> Select[_T]:
    field: SQLColumnExpression[Any]
    match sort.field:
        case MangaSortField.title:
            field = Manga.title
        case MangaSortField.created_at:
            field = Manga.created_at
        case MangaSortField.chapter_upload:
            field = MangaChapter.created_at
            stmt = stmt.join(Manga.latest_chapter, isouter=True).group_by(
                MangaChapter.created_at,
            )
        case _:  # pragma: no cover
            assert_never(sort)
    field = field if sort.direction is SortDirection.asc else field.desc()
    id_field = (
        Manga.id if sort.direction is SortDirection.asc else Manga.id.desc()
    )
    return stmt.order_by(field.nulls_last(), id_field)


def filter_manga_stmt(
    stmt: Select[_T],
    filter: MangaFilter,
) -> Select[_T]:
    stmt = stmt.group_by(Manga.id)
    if filter.statuses:
        stmt = stmt.where(Manga.status.in_(filter.statuses))

    if filter.search_term:
        stmt = stmt.join(Manga.alt_titles, isouter=True).where(
            or_(
                AltTitle.title.op("&@~")(filter.search_term),
                Manga.title.op("&@~")(filter.search_term),
            ),
        )
    if filter.tags.include:
        include_alias = aliased(MangaTag, name="tags_include")
        stmt = (
            stmt.join(include_alias, Manga.tags)
            .where(include_alias.id.in_(filter.tags.include))
            .having(
                func.count(include_alias.id) >= len(filter.tags.include),
            )
        )
    if filter.tags.exclude:
        exclude_alias = aliased(MangaTag, name="tags_exclude")
        stmt = stmt.join(
            exclude_alias,
            Manga.tags.and_(
                exclude_alias.id.in_(filter.tags.exclude),
            ),
            isouter=True,
        ).having(func.count(exclude_alias.id) == 0)

    return stmt


class MangaRepository:
    _base_stmt = select(Manga).where(Manga.is_public.is_(True))

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self,
        id: UUID,
        options: Sequence[ORMOption] = (),
    ) -> Manga | None:
        stmt = self._base_stmt.where(Manga.id == id).options(*options)
        return (await self._session.scalars(stmt)).one_or_none()

    async def find_any(
        self,
        filter: MangaFindFilter,
    ) -> Manga | None:
        stmt = select(Manga).limit(2)

        where_clauses = []
        if filter.title is not None:  # pragma: no branch
            where_clauses.append(Manga.title == filter.title)
        if filter.title_slug is not None:  # pragma: no branch
            where_clauses.append(Manga.title_slug == filter.title_slug)
        stmt = stmt.where(or_(*where_clauses))

        return (await self._session.scalars(stmt)).one_or_none()

    async def paginate(
        self,
        *,
        filter: MangaFilter | None = None,
        sort: Sort[MangaSortField],
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[Manga]:
        stmt = self._base_stmt
        if filter:
            stmt = filter_manga_stmt(stmt=stmt, filter=filter)
        stmt = sort_manga_stmt(stmt=stmt, sort=sort)
        return await page_paginate(
            session=self._session,
            stmt=stmt,
            pagination=pagination,
        )
