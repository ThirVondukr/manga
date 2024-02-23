from app.core.domain.manga.dto import MangaCreateDTO
from app.core.domain.manga.services import MangaService
from app.db.models import Manga


class MangaCreateCommand:
    def __init__(self, manga_service: MangaService) -> None:
        self._manga_service = manga_service

    async def execute(self, dto: MangaCreateDTO) -> Manga:
        return await self._manga_service.create(dto=dto)
