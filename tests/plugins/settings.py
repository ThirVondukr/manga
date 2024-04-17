import pytest

from app.settings import AuthSettings, ImageSettings, TestAuthSettings
from lib.settings import get_settings


@pytest.fixture(scope="session")
async def auth_settings() -> AuthSettings:
    return get_settings(AuthSettings)


@pytest.fixture(scope="session")
def test_auth_settings() -> TestAuthSettings:
    return get_settings(TestAuthSettings)


@pytest.fixture(scope="session")
async def image_settings() -> ImageSettings:
    return get_settings(ImageSettings)
