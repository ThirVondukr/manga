from app.core.domain.manga.manga.filters import (
    MangaFilter,
    MangaSortField,
    Sort,
)
from app.core.domain.manga.manga.repositories import MangaRepository
from app.db.models.manga import Manga
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)


class MangaSearchQuery:
    def __init__(self, repository: MangaRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        *,
        filter: MangaFilter,
        pagination: PagePaginationParamsDTO,
        sort: Sort[MangaSortField],
    ) -> PagePaginationResultDTO[Manga]:
        return await self._repository.paginate(
            filter=filter,
            pagination=pagination,
            sort=sort,
        )
