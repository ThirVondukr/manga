from collections.abc import Sequence

from app.core.domain.manga.tags.repository import MangaTagRepository
from app.db.models.manga import MangaTag


class AllMangaTagsQuery:
    def __init__(self, repository: MangaTagRepository) -> None:
        self._repository = repository

    async def execute(self) -> Sequence[MangaTag]:
        return await self._repository.all()
