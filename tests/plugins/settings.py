import pytest

from app.settings import AuthSettings, ImageSettings
from tests.types import Resolver


@pytest.fixture
async def auth_settings(resolver: Resolver) -> AuthSettings:
    return await resolver(AuthSettings)


@pytest.fixture
async def image_settings(resolver: Resolver) -> ImageSettings:
    return await resolver(ImageSettings)
