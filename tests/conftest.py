from collections.abc import AsyncIterator

import dotenv
import httpx
import pytest
from fastapi import FastAPI

dotenv.load_dotenv(".env")
pytest_plugins = [
    "anyio",
    "tests.conftest_db",
    "tests.conftest_services",
]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def fastapi_app() -> FastAPI:
    from api.app import create_app

    return create_app()


@pytest.fixture
async def http_client(fastapi_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=fastapi_app,
        base_url="http://test",
    ) as client:
        yield client
