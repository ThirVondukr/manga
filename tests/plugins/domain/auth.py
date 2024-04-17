import uuid
from datetime import timedelta

import jwt
import pytest

from app.core.domain.auth.dto import TokenClaims, TokenWrapper
from app.core.domain.auth.services import TokenService
from app.db.models import User
from app.settings import AuthSettings, TestAuthSettings
from lib.db import DBContext
from lib.time import utc_now
from tests.types import Resolver


@pytest.fixture
async def token_service(resolver: Resolver) -> TokenService:
    return await resolver(TokenService)


@pytest.fixture(scope="session")
async def user_token(
    auth_settings: AuthSettings,
    test_auth_settings: TestAuthSettings,
) -> TokenWrapper:
    now = utc_now()
    claims = TokenClaims(
        sub=uuid.uuid4(),
        aud=auth_settings.audience,
        email="test@example.com",
        exp=now + timedelta(minutes=10),
        iat=now,
        preferred_username="test",
        typ="Bearer",
    )
    token = jwt.encode(
        payload=claims.model_dump(mode="json"),
        key=test_auth_settings.private_key,
        algorithm=auth_settings.algorithm,
    )
    return TokenWrapper(
        token=token,
        claims=claims,
    )


@pytest.fixture
async def user(
    user_token: TokenWrapper,
    db_context: DBContext,
) -> User:
    user = User(
        id=user_token.claims.sub,
        username=user_token.claims.preferred_username,
        email=user_token.claims.email,
        password_hash="",
    )
    db_context.add(user)
    return user


@pytest.fixture
async def make_user_superuser(user: User, db_context: DBContext) -> User:
    user.is_superuser = True
    db_context.add(user)
    return user


@pytest.fixture
async def other_user(db_context: DBContext) -> User:
    user = User(
        id=uuid.uuid4(),
        username="User_2",
        email="user_2@example.com",
        password_hash="",
    )
    db_context.add(user)
    return user
