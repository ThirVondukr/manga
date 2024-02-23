import uuid

import pytest
from passlib.context import CryptContext
from pydantic import SecretStr

from app.core.domain.auth.dto import UserRegisterDTO
from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.errors import UserAlreadyExistsError
from app.db.models import User
from tests.types import Resolver

pytestmark = [pytest.mark.usefixtures("session")]


@pytest.fixture
async def command(resolver: Resolver) -> UserRegisterCommand:
    return await resolver(UserRegisterCommand)


async def test_ok(
    command: UserRegisterCommand,
    crypt_context: CryptContext,
) -> None:
    password = str(uuid.uuid4())
    dto = UserRegisterDTO(
        email="email@example.com",
        password=SecretStr(password),
        username="user",
    )
    result = (await command.execute(dto)).unwrap()
    assert result.user.email == dto.email
    assert result.user.username == dto.username
    assert crypt_context.verify(secret=password, hash=result.user.password_hash)


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
