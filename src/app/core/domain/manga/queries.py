from app.core.domain.manga.filters import MangaFilter
from app.core.domain.manga.repositories import MangaRepository
from app.db.models import Manga
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)


class MangaSearchQuery:
    def __init__(self, repository: MangaRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        filter: MangaFilter,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[Manga]:
        return await self._repository.paginate(
            filter=filter,
            pagination=pagination,
        )
