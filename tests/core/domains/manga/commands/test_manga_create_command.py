import uuid

import pytest
from slugify import slugify

from app.core.domain.manga.commands import MangaCreateCommand
from app.core.domain.manga.dto import MangaCreateDTO
from app.core.errors import EntityAlreadyExistsError, PermissionDeniedError
from app.db.models import Manga, User
from lib.types import MangaStatus
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaCreateCommand:
    return await resolver(MangaCreateCommand)


@pytest.fixture
def dto(manga_status: MangaStatus) -> MangaCreateDTO:
    return MangaCreateDTO(title=str(uuid.uuid4()), status=manga_status)


async def test_should_be_superuser(
    command: MangaCreateCommand,
    user: User,
    dto: MangaCreateDTO,
) -> None:
    assert not user.is_superuser

    err = (await command.execute(dto=dto, user=user)).unwrap_err()
    assert err == PermissionDeniedError()


@pytest.mark.usefixtures("make_user_superuser")
async def test_manga_exists(
    command: MangaCreateCommand,
    user: User,
    manga: Manga,
    dto: MangaCreateDTO,
) -> None:
    dto.title = manga.title

    err = (await command.execute(dto=dto, user=user)).unwrap_err()
    assert err == EntityAlreadyExistsError()


@pytest.mark.usefixtures("make_user_superuser")
async def test_ok(
    command: MangaCreateCommand,
    user: User,
    manga_status: MangaStatus,
    dto: MangaCreateDTO,
) -> None:
    manga = (await command.execute(dto=dto, user=user)).unwrap()
    assert manga.title == dto.title
    assert manga.title_slug == slugify(dto.title)
    assert manga.status == manga_status
