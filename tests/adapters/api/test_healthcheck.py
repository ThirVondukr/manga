from http import HTTPStatus

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.anyio]


async def test_healthcheck(http_client: AsyncClient) -> None:
    response = await http_client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() is None
