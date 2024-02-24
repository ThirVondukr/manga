import collections
from collections.abc import Sequence
from typing import Protocol, TypeVar, final
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql.elements import SQLCoreOperations

from app.db.models import AltTitle, Manga, MangaTag
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


class SQLAListLoader(LoaderProtocol[K, Sequence[V]], Protocol):
    column: SQLCoreOperations[K]
    stmt: Select[tuple[K, V]]

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, keys: Sequence[K]) -> Sequence[Sequence[V]]:
        stmt = self.stmt.where(self.__class__.column.in_(keys))
        models = collections.defaultdict(list)
        for key, model in await self._session.execute(stmt):
            models[key].append(model)
        return [models[key] for key in keys]


class MangaAltTitleLoader(SQLAListLoader[UUID, AltTitle]):
    column = Manga.id
    stmt = (
        select(Manga.id, AltTitle)
        .join(AltTitle.manga)
        .order_by(AltTitle.language, AltTitle.id)
    )


@final
class MangaLoader(SQLALoader[UUID, Manga]):
    column = Manga.id
    stmt = select(Manga)


class MangaTagLoader(SQLAListLoader[UUID, MangaTag]):
    column = manga_manga_tag_secondary_table.c.manga_id
    stmt = (
        select(
            manga_manga_tag_secondary_table.c.manga_id,
            MangaTag,
        )
        .join(
            manga_manga_tag_secondary_table,
            manga_manga_tag_secondary_table.c.tag_id == MangaTag.id,
        )
        .order_by(
            MangaTag.name_slug,
        )
    )
