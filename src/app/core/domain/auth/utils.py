import asyncio
from collections.abc import Generator

import aioinject

from app.core.domain.auth.dto import TokenClaims
from app.core.domain.users.filters import UserFilter
from app.core.domain.users.repositories import UserRepository
from app.db.models import User


class UserGetter:
    def __init__(
        self,
        container: aioinject.Container,
        token: TokenClaims | None,
    ) -> None:
        self._container = container
        self._token = token
        self._lock = asyncio.Lock()
        self._cache: User | None = None

    async def _fetch_user(self) -> User:
        if self._token is None:
            raise ValueError

        if not self._cache:
            async with self._lock:
                if not self._cache:
                    async with self._container.context() as ctx:
                        repo = await ctx.resolve(UserRepository)
                        user = await repo.get(
                            filter=UserFilter(id=self._token.sub),
                        )
                    if not user:
                        raise ValueError
                    self._cache = user
        return self._cache

    def __await__(self) -> Generator[None, None, User]:
        return self._fetch_user().__await__()
