from uuid import UUID

from sqlalchemy import Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.models import AltTitle, Manga, MangaTag
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate

from .filters import MangaFilter


class MangaRepository:
    _base_stmt = select(Manga).where(Manga.is_public.is_(True))

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: UUID) -> Manga | None:
        stmt = self._base_stmt.where(Manga.id == id)
        return (await self._session.scalars(stmt)).one_or_none()

    async def paginate(
        self,
        filter: MangaFilter,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[Manga]:
        await self._session.execute(text("set enable_seqscan = off;"))
        stmt = self._filter_stmt(filter=filter)
        return await page_paginate(
            session=self._session,
            stmt=stmt,
            pagination=pagination,
        )

    def _filter_stmt(self, filter: MangaFilter) -> Select[tuple[Manga]]:
        stmt = self._base_stmt.group_by(Manga.id).order_by(
            Manga.title,
            Manga.id,
        )
        if filter.search_term:
            stmt = stmt.join(Manga.alt_titles, isouter=True).where(
                AltTitle.title.op("&@~")(filter.search_term),
            )
        if filter.tags.include:
            include_alias = aliased(MangaTag, name="tags_include")
            stmt = (
                stmt.join(include_alias, Manga.tags)
                .where(include_alias.name_slug.in_(filter.tags.include))
                .having(
                    func.count(include_alias.id) >= len(filter.tags.include),
                )
            )
        if filter.tags.exclude:
            exclude_alias = aliased(MangaTag, name="tags_exclude")
            stmt = stmt.join(
                exclude_alias,
                Manga.tags.and_(
                    exclude_alias.name_slug.in_(filter.tags.exclude),
                ),
                isouter=True,
            ).having(func.count(exclude_alias.id) == 0)

        return stmt
