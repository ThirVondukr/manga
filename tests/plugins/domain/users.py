import pytest

from app.core.domain.users.repositories import UserRepository
from tests.types import Resolver


@pytest.fixture
async def user_repository(resolver: Resolver) -> UserRepository:
    return await resolver(UserRepository)
