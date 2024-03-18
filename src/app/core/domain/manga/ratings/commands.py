from result import Result

from app.core.domain.manga.ratings.dto import (
    MangaSetRatingDTO,
    MangaSetRatingResult,
)
from app.core.domain.manga.ratings.services import MangaRatingService
from app.core.errors import NotFoundError
from app.db.models import User
from lib.db import DBContext


class MangaSetRatingCommand:
    def __init__(
        self,
        service: MangaRatingService,
        db_context: DBContext,
    ) -> None:
        self._service = service
        self._db_context = db_context

    async def execute(
        self,
        dto: MangaSetRatingDTO,
        user: User,
    ) -> Result[MangaSetRatingResult, NotFoundError]:
        result = await self._service.set_rating(dto=dto, user=user)
        await self._db_context.flush()
        return result
