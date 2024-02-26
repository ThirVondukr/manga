import uuid

import pytest

from app.core.domain.groups.commands import GroupCreateCommand
from app.core.domain.groups.dto import GroupCreateDTO
from app.core.errors import EntityAlreadyExistsError
from app.db.models import Group, User
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> GroupCreateCommand:
    return await resolver(GroupCreateCommand)


async def test_group_already_exists(
    user: User,
    group: Group,
    command: GroupCreateCommand,
) -> None:
    result = await command.execute(
        user=user,
        dto=GroupCreateDTO(name=group.name),
    )
    assert result.unwrap_err() == EntityAlreadyExistsError()


async def test_ok(
    user: User,
    command: GroupCreateCommand,
) -> None:
    name = str(uuid.uuid4())
    result = await command.execute(
        user=user,
        dto=GroupCreateDTO(name=name),
    )
    group = result.unwrap()
    assert group.name == name
    assert group.created_by == user
