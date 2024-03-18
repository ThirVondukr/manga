from result import Err, Ok, Result

from app.core.domain.manga.manga.repositories import MangaRepository
from app.core.domain.manga.ratings.dto import (
    MangaSetRatingDTO,
    MangaSetRatingResult,
)
from app.core.domain.manga.ratings.repositories import MangaRatingRepository
from app.core.errors import NotFoundError
from app.db.models import MangaRating, User
from lib.db import DBContext


class MangaRatingService:
    def __init__(
        self,
        manga_repository: MangaRepository,
        rating_repository: MangaRatingRepository,
        db_context: DBContext,
    ) -> None:
        self._manga_repository = manga_repository
        self._rating_repository = rating_repository
        self._db_context = db_context

    async def set_rating(
        self,
        dto: MangaSetRatingDTO,
        user: User,
    ) -> Result[MangaSetRatingResult, NotFoundError]:
        if (manga := await self._manga_repository.get(id=dto.manga_id)) is None:
            return Err(NotFoundError(entity_id=str(dto.manga_id)))

        await self._rating_repository.delete_rating(
            user_id=user.id,
            manga=manga,
        )
        if dto.rating is None:
            return Ok(MangaSetRatingResult(manga=manga, rating=None))

        rating = MangaRating(
            rating=dto.rating,
            manga=manga,
            user=user,
        )
        await self._rating_repository.add_rating(
            manga=manga,
            rating=dto.rating,
        )
        self._db_context.add(rating)
        return Ok(MangaSetRatingResult(manga=manga, rating=rating))
