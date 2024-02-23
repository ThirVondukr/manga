from collections.abc import Sequence
from typing import Protocol, TypeVar, final
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute

from app.db.models import Manga
from lib.loaders import LoaderProtocol

K = TypeVar("K")
V = TypeVar("V")


class SQLALoader(LoaderProtocol[K, V | None], Protocol):
    column: QueryableAttribute[K]
    stmt: Select[tuple[V]]

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, keys: Sequence[K]) -> Sequence[V | None]:
        stmt = self.stmt.where(self.__class__.column.in_(keys))
        models = {
            getattr(model, self.__class__.column.key): model
            for model in await self._session.scalars(stmt)
        }
        return [models.get(key) for key in keys]


@final
class MangaLoader(SQLALoader[UUID, Manga]):
    column = Manga.id
    stmt = select(Manga)
