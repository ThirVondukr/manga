import uuid

import pytest

from app.core.domain.auth.services import AuthService
from app.core.domain.users.repositories import UserRepository
from tests.types import Resolver


@pytest.fixture
async def auth_service(resolver: Resolver) -> AuthService:
    return await resolver(AuthService)


@pytest.fixture
async def user_repository(resolver: Resolver) -> UserRepository:
    return await resolver(UserRepository)


@pytest.fixture
async def user_password() -> str:
    return str(uuid.uuid4())
