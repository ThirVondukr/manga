import uuid

import pytest

from app.core.domain.branches.commands import MangaBranchCreateCommand
from app.core.domain.branches.dto import MangaBranchCreateDTO
from app.core.errors import RelationshipNotFoundError
from app.db.models import Group, Manga, User
from lib.types import Language
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaBranchCreateCommand:
    return await resolver(MangaBranchCreateCommand)


@pytest.fixture
def dto(language: Language) -> MangaBranchCreateDTO:
    return MangaBranchCreateDTO(
        manga_id=uuid.uuid4(),
        group_id=uuid.uuid4(),
        name=str(uuid.uuid4()),
        language=language,
    )


async def test_manga_not_found(
    command: MangaBranchCreateCommand,
    dto: MangaBranchCreateDTO,
    user: User,
) -> None:
    result = await command.execute(dto=dto, user=user)
    assert result.unwrap_err() == RelationshipNotFoundError(
        entity_id=str(dto.manga_id),
        entity_name="Manga",
    )


async def test_group_not_found(
    command: MangaBranchCreateCommand,
    dto: MangaBranchCreateDTO,
    user: User,
    manga: Manga,
) -> None:
    dto.manga_id = manga.id
    result = await command.execute(dto=dto, user=user)
    assert result.unwrap_err() == RelationshipNotFoundError(
        entity_id=str(dto.group_id),
        entity_name="MangaBranch",
    )


async def test_ok(
    command: MangaBranchCreateCommand,
    dto: MangaBranchCreateDTO,
    manga: Manga,
    group: Group,
    user: User,
) -> None:
    dto.group_id = group.id
    dto.manga_id = manga.id
    result = await command.execute(dto=dto, user=user)
    branch = result.unwrap()

    assert branch.manga is manga
    assert branch.name == dto.name
    assert branch.language == dto.language
