import pytest

from app.core.domain.users.filters import UserFilter
from app.core.domain.users.repositories import UserRepository

pytestmark = pytest.mark.anyio


@pytest.mark.usefixtures("user")
async def test_exists_ok(user_repository: UserRepository) -> None:
    assert await user_repository.exists(filter=UserFilter()) is True


async def test_exists_empty(user_repository: UserRepository) -> None:
    assert await user_repository.exists(filter=UserFilter()) is False
