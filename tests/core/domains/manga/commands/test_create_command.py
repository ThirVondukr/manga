import uuid

import pytest
from slugify import slugify

from app.core.domain.manga.commands import MangaCreateCommand
from app.core.domain.manga.dto import MangaCreateDTO
from app.db.models import User
from lib.types import MangaStatus
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaCreateCommand:
    return await resolver(MangaCreateCommand)


async def test_ok(
    command: MangaCreateCommand,
    user: User,
    manga_status: MangaStatus,
) -> None:
    dto = MangaCreateDTO(title=str(uuid.uuid4()), status=manga_status)
    manga = await command.execute(dto=dto, user=user)
    assert manga.title == dto.title
    assert manga.title_slug == slugify(dto.title)
    assert manga.status == manga_status
