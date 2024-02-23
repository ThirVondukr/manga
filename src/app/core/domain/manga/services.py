import uuid

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga

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
