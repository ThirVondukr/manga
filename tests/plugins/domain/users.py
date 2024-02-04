import uuid

import pytest
from pydantic import SecretStr

from app.core.domain.users.dto import UserRegisterDTO
from app.core.domain.users.repositories import UserRepository
from app.core.domain.users.services import UserService
from app.db.models import User
from tests.types import Resolver


@pytest.fixture
async def user_service(resolver: Resolver) -> UserService:
    return await resolver(UserService)


@pytest.fixture
async def user_repository(resolver: Resolver) -> UserRepository:
    return await resolver(UserRepository)


@pytest.fixture
async def user_password() -> str:
    return str(uuid.uuid4())


@pytest.fixture
async def user(
    user_service: UserService,
    user_password: str,
) -> User:
    user = await user_service.register(
        dto=UserRegisterDTO(
            username=str(uuid.uuid4()),
            email="email@example.org",
            password=SecretStr(user_password),
        ),
    )
    return user.unwrap()
