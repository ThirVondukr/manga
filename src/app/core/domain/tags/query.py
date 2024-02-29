from collections.abc import Sequence

from app.core.domain.tags.repository import MangaTagRepository
from app.db.models import MangaTag


class AllMangaTagsQuery:
    def __init__(self, repository: MangaTagRepository) -> None:
        self._repository = repository

    async def execute(self) -> Sequence[MangaTag]:
        return await self._repository.all()
