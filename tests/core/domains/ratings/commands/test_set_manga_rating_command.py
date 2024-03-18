import random
import uuid

import pytest

from app.core.domain.manga.ratings.commands import MangaSetRatingCommand
from app.core.domain.manga.ratings.dto import MangaSetRatingDTO
from app.core.errors import NotFoundError
from app.db.models import Manga, User
from tests.factories import UserFactory
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaSetRatingCommand:
    return await resolver(MangaSetRatingCommand)


@pytest.fixture
async def dto(manga: Manga) -> MangaSetRatingDTO:
    return MangaSetRatingDTO(
        manga_id=manga.id,
        rating=10,
    )


async def test_manga_not_found(
    command: MangaSetRatingCommand,
    user: User,
    dto: MangaSetRatingDTO,
) -> None:
    dto.manga_id = uuid.uuid4()
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == NotFoundError(entity_id=str(dto.manga_id))


async def test_ok(
    command: MangaSetRatingCommand,
    user: User,
    dto: MangaSetRatingDTO,
    manga: Manga,
) -> None:
    assert manga.rating == 0
    result = await command.execute(user=user, dto=dto)
    assert result.is_ok()

    assert manga.rating == dto.rating


async def test_cumulative_rating(
    command: MangaSetRatingCommand,
    manga: Manga,
) -> None:
    size = 100
    ratings = [random.randint(1, 10) for _ in range(size)]
    users = UserFactory.build_batch(size=size)
    ratings_and_users = list(zip(users, ratings, strict=True))

    for i, (user, rating) in enumerate(ratings_and_users, start=1):
        result = await command.execute(
            user=user,
            dto=MangaSetRatingDTO(manga_id=manga.id, rating=rating),
        )
        assert result.is_ok()
        assert manga.rating == pytest.approx(sum(ratings[:i]) / i)

    while ratings_and_users:
        user, rating = random.choice(ratings_and_users)
        ratings_and_users.remove((user, rating))

        expected_rating = sum(
            (rating for _, rating in ratings_and_users),
        ) / max(len(ratings_and_users), 1)

        result = await command.execute(
            user=user,
            dto=MangaSetRatingDTO(manga_id=manga.id, rating=None),
        )
        assert result.is_ok()
        assert manga.rating == pytest.approx(expected_rating)
