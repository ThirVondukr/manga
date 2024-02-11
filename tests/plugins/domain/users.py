import uuid

import pytest
from pydantic import SecretStr

from app.core.domain.auth.dto import UserRegisterDTO
from app.core.domain.auth.services import AuthService
from app.core.domain.users.repositories import UserRepository
from app.db.models import User
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


@pytest.fixture
async def user(
    auth_service: AuthService,
    user_password: str,
) -> User:
    user = await auth_service.sign_up(
        dto=UserRegisterDTO(
            username=str(uuid.uuid4()),
            email="email@example.org",
            password=SecretStr(user_password),
        ),
    )
    return user.unwrap()
