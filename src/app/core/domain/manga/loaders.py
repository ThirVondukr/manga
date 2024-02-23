import collections
from collections.abc import Sequence
from typing import Protocol, TypeVar, final
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute

from app.db.models import Manga, MangaTag
from app.db.models._manga import manga_manga_tag_secondary_table
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


class MangaTagLoader(LoaderProtocol[UUID, Sequence[MangaTag]]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(
        self,
        keys: Sequence[UUID],
    ) -> Sequence[Sequence[MangaTag]]:
        stmt = select(
            manga_manga_tag_secondary_table.c.manga_id,
            MangaTag,
        ).join(
            manga_manga_tag_secondary_table,
            manga_manga_tag_secondary_table.c.tag_id == MangaTag.id,
        )
        tags = collections.defaultdict(list)
        for manga_id, tag in await self._session.execute(stmt):
            tags[manga_id].append(tag)

        return [tags[key] for key in keys]
