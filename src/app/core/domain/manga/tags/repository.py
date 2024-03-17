from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MangaTag


class MangaTagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def all(self) -> Sequence[MangaTag]:
        stmt = select(MangaTag).order_by(MangaTag.name)
        return (await self._session.scalars(stmt)).all()
