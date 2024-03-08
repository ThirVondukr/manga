import uuid

import pytest
from slugify import slugify

from app.core.domain.manga.commands import MangaCreateCommand
from app.core.domain.manga.dto import MangaCreateDTO
from app.core.errors import EntityAlreadyExistsError
from app.db.models import Manga, User
from lib.types import MangaStatus
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaCreateCommand:
    return await resolver(MangaCreateCommand)


async def test_manga_exists(
    command: MangaCreateCommand,
    user: User,
    manga_status: MangaStatus,
    manga: Manga,
) -> None:
    dto = MangaCreateDTO(title=manga.title, status=manga_status)

    err = (await command.execute(dto=dto, user=user)).unwrap_err()
    assert err == EntityAlreadyExistsError()


async def test_ok(
    command: MangaCreateCommand,
    user: User,
    manga_status: MangaStatus,
) -> None:
    dto = MangaCreateDTO(title=str(uuid.uuid4()), status=manga_status)
    manga = (await command.execute(dto=dto, user=user)).unwrap()
    assert manga.title == dto.title
    assert manga.title_slug == slugify(dto.title)
    assert manga.status == manga_status
