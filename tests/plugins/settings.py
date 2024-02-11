import pytest

from app.settings import AuthSettings
from tests.types import Resolver


@pytest.fixture
async def auth_settings(resolver: Resolver) -> AuthSettings:
    return await resolver(AuthSettings)
