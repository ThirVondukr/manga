import httpx
import pytest

from tests.adapters.graphql.client import GraphQLClient


@pytest.fixture
async def graphql_client(http_client: httpx.AsyncClient) -> GraphQLClient:
    return GraphQLClient(
        client=http_client,
        endpoint="/graphql/",
    )
