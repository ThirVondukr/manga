import uuid

import pytest

from app.core.domain.manga.commands import MangaUpdateCommand
from app.core.domain.manga.dto import MangaUpdateDTO
from app.core.errors import (
    EntityAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.models import Manga, User
from lib.db import DBContext
from lib.types import MangaStatus
from tests.factories import MangaFactory
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaUpdateCommand:
    return await resolver(MangaUpdateCommand)


@pytest.fixture
def dto(manga_status: MangaStatus, manga: Manga) -> MangaUpdateDTO:
    return MangaUpdateDTO(
        id=manga.id,
        title=str(uuid.uuid4()),
        status=manga_status,
    )


async def test_permission_denied(
    command: MangaUpdateCommand,
    dto: MangaUpdateDTO,
    user: User,
) -> None:
    result = await command.execute(dto=dto, user=user)
    assert result.unwrap_err() == PermissionDeniedError()


async def test_manga_not_found(
    command: MangaUpdateCommand,
    dto: MangaUpdateDTO,
    user: User,
) -> None:
    dto.id = uuid.uuid4()
    result = await command.execute(dto=dto, user=user)
    assert result.unwrap_err() == NotFoundError(entity_id=str(dto.id))


@pytest.mark.usefixtures("make_user_superuser")
async def test_ok(
    command: MangaUpdateCommand,
    dto: MangaUpdateDTO,
    user: User,
) -> None:
    result = await command.execute(dto=dto, user=user)
    manga = result.unwrap()

    assert manga.title == dto.title
    assert manga.status == dto.status
    assert manga.status == dto.status


@pytest.mark.usefixtures("make_user_superuser")
async def test_title_is_taken(
    command: MangaUpdateCommand,
    dto: MangaUpdateDTO,
    user: User,
    db_context: DBContext,
) -> None:
    existing_manga = MangaFactory.build()
    db_context.add(existing_manga)

    dto.title = existing_manga.title
    result = await command.execute(dto=dto, user=user)
    assert result.unwrap_err() == EntityAlreadyExistsError()
