import httpx
import pytest

from tests.adapters.graphql.client import GraphQLClient


@pytest.fixture
async def graphql_client(http_client: httpx.AsyncClient) -> GraphQLClient:
    return GraphQLClient(
        client=http_client,
        endpoint="/graphql/",
    )


@pytest.fixture
async def authenticated_graphql_client(
    authenticated_http_client: httpx.AsyncClient,
) -> GraphQLClient:
    return GraphQLClient(
        client=authenticated_http_client,
        endpoint="/graphql/",
    )
