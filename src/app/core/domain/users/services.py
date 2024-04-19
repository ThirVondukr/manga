from typing import Literal

from result import Err, Ok, Result

from app.core.domain.auth.dto import TokenClaims
from app.core.domain.users.filters import UserFilter
from app.core.domain.users.repositories import UserRepository
from app.core.errors import PermissionDeniedError
from app.db.models import User
from lib.db import DBContext


class PermissionService:
    async def is_superuser_check(
        self,
        user: User,
    ) -> Result[Literal[True], PermissionDeniedError]:
        if not user.is_superuser:
            return Err(PermissionDeniedError())

        return Ok(user.is_superuser)


class UserService:
    def __init__(
        self,
        db_context: DBContext,
        user_repository: UserRepository,
    ) -> None:
        self._db_context = db_context
        self._user_repository = user_repository

    async def sync_token_data(self, claims: TokenClaims) -> User:
        user = await self._user_repository.get(filter=UserFilter(id=claims.sub))
        if not user:
            user = User(
                id=claims.sub,
                email=claims.email,
                username=claims.preferred_username,
            )
            self._db_context.add(user)
            return user

        if user.email != claims.email:
            user.email = claims.email

        if user.username != claims.preferred_username:
            user.username = claims.preferred_username

        self._db_context.add(user)
        return user
