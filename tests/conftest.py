import pkgutil
from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from typing import cast
from unittest.mock import patch

import aioinject
import dotenv
import httpx
import pytest
from _pytest.fixtures import SubRequest
from aioinject import Object
from asgi_lifespan import LifespanManager
from faker import Faker
from fastapi import FastAPI
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession

import tests.plugins
from app.core.di import create_container
from app.core.domain.auth.dto import TokenWrapper
from app.core.storage import FileStorage
from app.db.models import User
from app.settings import AuthSettings, TestAuthSettings
from lib.connectors.keycloak import KeycloakClient, RealmInfo
from lib.settings import get_settings
from lib.time import utc_now
from tests.types import Resolver
from tests.utils import TestFileStorage

dotenv.load_dotenv(".env")

pytest_plugins = [
    "anyio",
    "sqlalchemy_pytest.database",
    *(
        mod.name
        for mod in pkgutil.walk_packages(
            tests.plugins.__path__,
            prefix="tests.plugins.",
        )
        if not mod.ispkg
    ),
]


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def http_app() -> AsyncIterator[FastAPI]:
    from app.adapters.api.app import create_app

    app = create_app()
    async with LifespanManager(app):
        yield app


@pytest.fixture
async def http_transport(
    http_app: FastAPI,
) -> AsyncIterator[httpx.AsyncBaseTransport]:
    async with httpx.ASGITransport(
        app=http_app,  # type: ignore[arg-type]
    ) as transport:
        yield transport


@pytest.fixture
async def http_client(
    http_transport: httpx.AsyncBaseTransport,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=http_transport,
        base_url="http://test",
    )


@pytest.fixture
async def authenticated_http_client(
    http_transport: httpx.AsyncBaseTransport,
    user: User,  # noqa: ARG001
    user_token: TokenWrapper,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=http_transport,
        base_url="http://test",
        headers={
            "authorization": f"Bearer {user_token.token}",
        },
    )


@pytest.fixture(scope="session")
def worker_id() -> str:
    return "main"


@pytest.fixture(scope="session")
async def container() -> AsyncIterator[aioinject.Container]:
    async with create_container() as container:
        yield container


@pytest.fixture(autouse=True)
async def resolver(
    container: aioinject.Container,
    session: AsyncSession,
) -> AsyncIterator[Resolver]:
    with container.override(Object(session, AsyncSession)):
        async with container.context() as ctx:
            yield ctx.resolve


@pytest.fixture
def now() -> datetime:
    return utc_now()


@pytest.fixture(params=[0, 1, 10])
def collection_size(request: SubRequest) -> int:
    return cast(int, request.param)


@pytest.fixture(autouse=True)
def s3_mock(container: aioinject.Container) -> Iterator[TestFileStorage]:
    storage = TestFileStorage()
    with container.override(Object(storage, type_=FileStorage)):
        yield storage


@pytest.fixture(autouse=True)
def _keycloak_mock(auth_settings: AuthSettings) -> Iterator[None]:
    settings = get_settings(TestAuthSettings)

    url = Url("https://127.0.0.1")

    async def realm_func(
        self: KeycloakClient,  # noqa: ARG001
        realm: str,
    ) -> RealmInfo:
        return RealmInfo(
            realm=realm,
            public_key=settings.public_key.removeprefix(
                auth_settings.public_key_begin,
            ).removesuffix(auth_settings.public_key_end),
            token_service=url,
            account_service=url,
            tokens_not_before=0,
        )

    with patch.object(
        KeycloakClient,
        KeycloakClient.realm_info.__name__,
        realm_func,
    ):
        yield


@pytest.fixture
def fake() -> Faker:
    return Faker()
