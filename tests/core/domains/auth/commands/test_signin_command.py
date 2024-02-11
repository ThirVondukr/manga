import pytest
from pydantic import SecretStr

from app.core.domain.auth.commands import SignInCommand
from app.core.domain.auth.dto import SignInDTO
from app.db.models import User
from tests.types import Resolver

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("session")]


@pytest.fixture
async def command(resolver: Resolver) -> SignInCommand:
    return await resolver(SignInCommand)


async def test_ok(
    command: SignInCommand,
    user: User,
    user_password: str,
) -> None:
    result = await command.execute(
        dto=SignInDTO(email=user.email, password=SecretStr(user_password)),
    )
    assert result is not None
    assert result.user is user


async def test_invalid_password(
    command: SignInCommand,
    user: User,
    user_password: str,
) -> None:
    result = await command.execute(
        dto=SignInDTO(
            email=user.email,
            password=SecretStr(user_password + " "),
        ),
    )
    assert result is None


async def test_invalid_credentials(
    command: SignInCommand,
) -> None:
    result = await command.execute(
        dto=SignInDTO(email="user@example.com", password=SecretStr("")),
    )
    assert result is None
