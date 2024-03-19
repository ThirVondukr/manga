from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.manga import MangaBranch, MangaChapter
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate


class ChapterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_one(
        self,
        number: Sequence[int] | None = None,
        branch_id: UUID | None = None,
    ) -> MangaChapter | None:
        stmt = select(MangaChapter).limit(2)
        if number:  # pragma: no branch
            stmt = stmt.where(MangaChapter.number == number)
        if branch_id:  # pragma: no branch
            stmt = stmt.where(MangaChapter.branch_id == branch_id)

        return (await self._session.scalars(stmt)).one_or_none()

    async def paginate(
        self,
        manga_id: UUID,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[MangaChapter]:
        stmt = (
            select(MangaChapter)
            .order_by(MangaChapter.number.desc())
            .join(MangaBranch)
            .where(MangaBranch.manga_id == manga_id)
        )
        return await page_paginate(
            session=self._session,
            stmt=stmt,
            pagination=pagination,
        )
