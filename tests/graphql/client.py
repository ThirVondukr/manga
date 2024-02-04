from collections.abc import Mapping
from typing import Any, NotRequired, TypedDict, cast

import httpx


class GraphQLResponse(TypedDict):
    data: dict[str, Any]
    errors: NotRequired[Any]


class GraphQLClient:
    def __init__(self, client: httpx.AsyncClient, endpoint: str) -> None:
        self._client = client
        self._endpoint = endpoint

    async def query(
        self,
        query: str,
        variables: Mapping[str, Any] | None = None,
    ) -> GraphQLResponse:
        response = await self._client.post(
            self._endpoint,
            json={
                "query": query,
                "variables": variables,
            },
        )
        response.raise_for_status()
        return cast(GraphQLResponse, response.json())
