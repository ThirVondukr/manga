import uuid

import aioinject
import pytest
from pydantic import SecretStr

from app.core.domain.auth.dto import TokenWrapper, UserRegisterDTO
from app.core.domain.auth.services import AuthService, TokenService
from app.db.models import User
from lib.db import DBContext
from tests.types import Resolver


@pytest.fixture
async def token_service(resolver: Resolver) -> TokenService:
    return await resolver(TokenService)


@pytest.fixture(scope="session")
async def user_token(container: aioinject.Container) -> TokenWrapper:
    async with container.context() as ctx:
        token_service = await ctx.resolve(TokenService)
        return token_service.create_access_token(
            user=User(username="", email="", password_hash=""),
        )


@pytest.fixture
async def user(
    user_token: TokenWrapper,
    db_context: DBContext,
    user_password: str,
    auth_service: AuthService,
) -> User:
    result = await auth_service.sign_up(
        dto=UserRegisterDTO(
            username=str(uuid.uuid4()),
            email="email@example.org",
            password=SecretStr(user_password),
        ),
    )
    user = result.unwrap()
    user.id = user_token.claims.sub
    db_context.add(user)
    await db_context.flush()
    return user
