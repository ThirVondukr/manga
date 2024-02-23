import uuid
from collections.abc import Sequence

from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select

from app.db.models import Manga, MangaInfo, MangaTag

from .dto import MangaCreateDTO


class MangaService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self,
        entity_id: uuid.UUID | None = None,
        title_slug: str | None = None,
    ) -> Manga | None:
        if not any([entity_id, title_slug]):
            return None

        stmt = select(Manga).limit(1)
        if entity_id:
            stmt = stmt.where(Manga.id == entity_id)
        if title_slug:
            stmt = stmt.where(Manga.title_slug == title_slug)

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, dto: MangaCreateDTO) -> Manga:
        model = Manga(
            title=dto.title,
            title_slug=slugify(dto.title),
        )
        self._session.add(model)
        await self._session.flush()
        return model


class MangaSearchService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def search_query(
        self,
        search_term: str | None = None,
        tags_include: list[str] | None = None,
        tags_exclude: list[str] | None = None,
    ) -> Select[tuple[Manga]]:
        query = func.plainto_tsquery(search_term)
        stmt = (
            select(Manga)
            .group_by(Manga.id)
            .order_by(Manga.created_at.desc(), Manga.id)
        )
        if search_term:
            stmt = (
                stmt.join(Manga.info)
                .group_by(MangaInfo.search_ts_vector)
                .where(MangaInfo.search_ts_vector.op("@@")(query))
                .order_by(None)
                .order_by(
                    func.ts_rank_cd(MangaInfo.search_ts_vector, query).desc(),
                )
            )
        if tags_include:
            include_alias = aliased(MangaTag, name="tags_include")
            stmt = (
                stmt.join(include_alias, Manga.tags)
                .where(include_alias.name_slug.in_(tags_include))
                .having(func.count(include_alias.id) >= len(tags_include))
            )
        if tags_exclude:
            exclude_alias = aliased(MangaTag, name="tags_exclude")
            stmt = stmt.join(
                exclude_alias,
                Manga.tags.and_(exclude_alias.name_slug.in_(tags_exclude)),
                isouter=True,
            ).having(func.count(exclude_alias.id) == 0)
        return stmt


class MangaApprovalService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def _query(self) -> Select[tuple[Manga]]:
        return (
            select(Manga)
            .where(Manga.is_public.is_(other=False))
            .execution_options(include_private=True)
        )

    async def all(self) -> Sequence[Manga]:
        return (await self._session.scalars(self._query)).all()
