from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MangaBranch, MangaChapter
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)
from lib.pagination.sqla import page_paginate


class MangaChapterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
