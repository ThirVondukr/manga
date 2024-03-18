from result import Result

from app.core.domain.manga.ratings.dto import (
    MangaSetRatingDTO,
    MangaSetRatingResult,
)
from app.core.domain.manga.ratings.services import MangaRatingService
from app.core.errors import NotFoundError
from app.db.models import User


class MangaSetRatingCommand:
    def __init__(self, service: MangaRatingService) -> None:
        self._service = service

    async def execute(
        self,
        dto: MangaSetRatingDTO,
        user: User,
    ) -> Result[MangaSetRatingResult, NotFoundError]:
        return await self._service.set_rating(dto=dto, user=user)
