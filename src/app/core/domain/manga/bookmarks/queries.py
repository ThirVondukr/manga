from app.core.domain.auth.dto import TokenClaims
from app.core.domain.manga.bookmarks.repositories import BookmarkRepository
from app.db.models.manga import MangaBookmark
from lib.pagination.pagination import (
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)


class UserBookmarksQuery:
    def __init__(self, repository: BookmarkRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        user: TokenClaims,
        pagination: PagePaginationParamsDTO,
    ) -> PagePaginationResultDTO[MangaBookmark]:
        return await self._repository.user_bookmarks(
            user_id=user.sub,
            pagination=pagination,
        )
