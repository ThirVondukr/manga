import random
import uuid

import pytest

from app.core.domain.manga.art.command import MangaSetCoverArtCommand
from app.core.domain.manga.art.dto import MangaSetCoverArtDTO
from app.core.errors import NotFoundError, PermissionDeniedError
from app.db.models import User
from app.db.models.manga import Manga
from tests.factories import MangaArtFactory
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaSetCoverArtCommand:
    return await resolver(MangaSetCoverArtCommand)


@pytest.fixture
async def dto(manga: Manga) -> MangaSetCoverArtDTO:
    return MangaSetCoverArtDTO(
        manga_id=manga.id,
        art_id=uuid.uuid4(),
    )


async def test_manga_not_found(
    command: MangaSetCoverArtCommand,
    dto: MangaSetCoverArtDTO,
    user: User,
) -> None:
    dto.manga_id = uuid.uuid4()
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == NotFoundError(entity_id=str(dto.manga_id))


async def test_permission_denied(
    command: MangaSetCoverArtCommand,
    dto: MangaSetCoverArtDTO,
    user: User,
) -> None:
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == PermissionDeniedError()


@pytest.mark.usefixtures("make_user_superuser")
async def test_art_not_found(
    command: MangaSetCoverArtCommand,
    dto: MangaSetCoverArtDTO,
    user: User,
) -> None:
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == NotFoundError(entity_id=str(dto.art_id))


@pytest.mark.usefixtures("make_user_superuser")
async def test_ok(
    command: MangaSetCoverArtCommand,
    dto: MangaSetCoverArtDTO,
    user: User,
    manga: Manga,
) -> None:
    manga.arts = MangaArtFactory.build_batch(size=10)
    target_art = random.choice(manga.arts)

    # Test setting cover
    dto.art_id = target_art.id
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap() is manga
    assert manga.cover_art == target_art

    # Test setting cover to None
    dto.art_id = None
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap() is manga
    assert manga.cover_art is None
