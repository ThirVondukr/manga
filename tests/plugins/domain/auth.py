import pytest

from app.core.domain.auth.services import TokenService
from tests.types import Resolver


@pytest.fixture
async def token_service(resolver: Resolver) -> TokenService:
    return await resolver(TokenService)
