from uuid import UUID

from app.core.domain.manga.chapters.repositories import ChapterRepository
from app.db.models import MangaChapter
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)


class MangaChaptersQuery:
    def __init__(self, repository: ChapterRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        manga_id: UUID,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[MangaChapter]:
        return await self._repository.paginate(
            manga_id=manga_id,
            pagination=pagination,
        )
