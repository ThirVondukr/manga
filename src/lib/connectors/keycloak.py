import contextlib
import dataclasses
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated, Generic, Self, TypeVar

import httpx
from pydantic import BaseModel, ConfigDict, Field, UrlConstraints
from pydantic_core import Url

from lib.time import utc_now

HttpsUrl = Annotated[
    Url,
    UrlConstraints(max_length=2083, allowed_schemes=["https"]),
]
T = TypeVar("T")


class RealmInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    realm: str
    public_key: str
    token_service: Annotated[HttpsUrl, Field(alias="token-service")]
    account_service: Annotated[HttpsUrl, Field(alias="account-service")]
    tokens_not_before: Annotated[int, Field(alias="tokens-not-before")]


@dataclasses.dataclass(slots=True, kw_only=True)
class _Cached(Generic[T]):
    data: T
    expires_at: datetime


class KeycloakClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._cache_ttl = timedelta(days=1)
        self._realms: dict[str, _Cached[RealmInfo]] = {}

    @classmethod
    @contextlib.asynccontextmanager
    async def create(cls, base_url: str) -> AsyncIterator[Self]:
        async with httpx.AsyncClient(base_url=base_url) as client:
            yield cls(client=client)

    def _get_cached_realm(self, realm: str) -> RealmInfo | None:
        if cached := self._realms.get(realm):
            if cached.expires_at <= utc_now():
                del self._realms[realm]
                return None
            return cached.data
        return None

    async def realm_info(self, realm: str) -> RealmInfo | None:
        if cached := self._get_cached_realm(realm):
            return cached

        response = await self._client.get(f"/realms/{realm}")
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None
        response.raise_for_status()
        realm_info = RealmInfo.parse_raw(response.content)
        self._realms[realm] = _Cached(
            data=realm_info,
            expires_at=utc_now() + self._cache_ttl,
        )
        return realm_info
