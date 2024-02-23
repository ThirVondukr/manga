from slugify import slugify

from app.db.models import Manga
from lib.db import DBContext

from .dto import MangaCreateDTO


class MangaService:
    def __init__(
        self,
        db_context: DBContext,
    ) -> None:
        self._db_context = db_context

    async def create(self, dto: MangaCreateDTO) -> Manga:
        model = Manga(
            title=dto.title,
            title_slug=slugify(dto.title),
        )
        self._db_context.add(model)
        await self._db_context.flush()
        return model
