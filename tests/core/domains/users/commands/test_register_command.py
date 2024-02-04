import uuid

import pytest
from pydantic import SecretStr

from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.dto import UserRegisterDTO
from app.core.domain.users.errors import UserAlreadyExistsError
from app.db.models import User
from tests.types import Resolver

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("session")]


@pytest.fixture
async def command(resolver: Resolver) -> UserRegisterCommand:
    return await resolver(UserRegisterCommand)


async def test_ok(command: UserRegisterCommand) -> None:
    dto = UserRegisterDTO(
        email="email@example.com",
        password=SecretStr("pass"),
        username="user",
    )
    result = await command.execute(dto)
    user = result.unwrap()
    assert user.email == dto.email
    assert user.username == dto.username


async def test_user_exists(
    command: UserRegisterCommand,
    user: User,
) -> None:
    dto = UserRegisterDTO(
        email="shouldnotexist@example.com",
        username=str(uuid.uuid4()),
        password=SecretStr("pass"),
    )
    for key, value in (
        ("email", user.email),
        ("username", user.username),
    ):
        register_dto = dto.model_copy(update={key: value})
        result = await command.execute(register_dto)
        assert result.unwrap_err() == UserAlreadyExistsError()
