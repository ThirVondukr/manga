import dataclasses
from collections.abc import Awaitable
from functools import cached_property
from typing import TypeVar

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from strawberry.types import Info as StrawberryInfo
from strawberry.utils.await_maybe import await_maybe

from app.core.domain.auth.dto import TokenClaims
from app.db.models import User
from lib.loaders import Dataloaders

T = TypeVar("T")


@dataclasses.dataclass(kw_only=True)
class Context:
    request: Request | WebSocket
    response: Response | None
    loaders: Dataloaders

    maybe_access_token: TokenClaims | None
    _user: User | None

    @property
    def access_token(self) -> TokenClaims:
        if not self.maybe_access_token:  # pragma: no cover
            raise ValueError
        return self.maybe_access_token

    @cached_property
    def user(self) -> Awaitable[User]:
        if not self._user:
            raise ValueError  # pragma: no cover
        return await_maybe(self._user)


Info = StrawberryInfo[Context, None]
