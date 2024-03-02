import dataclasses
from collections.abc import Awaitable
from functools import cached_property
from typing import TypeVar

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from strawberry.types import Info as StrawberryInfo

from app.core.di import create_container
from app.core.domain.auth.dto import TokenClaims
from app.core.domain.auth.utils import UserGetter
from app.db.models import User
from lib.loaders import Dataloaders

T = TypeVar("T")


@dataclasses.dataclass(kw_only=True)
class Context:
    request: Request | WebSocket
    response: Response | None
    loaders: Dataloaders

    maybe_access_token: TokenClaims | None

    @property
    def access_token(self) -> TokenClaims:
        if not self.maybe_access_token:  # pragma: no cover
            raise ValueError
        return self.maybe_access_token

    @cached_property
    def user(self) -> Awaitable[User]:
        return UserGetter(
            container=create_container(),
            token=self.maybe_access_token,
        )


Info = StrawberryInfo[Context, None]
