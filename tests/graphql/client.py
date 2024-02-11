import dataclasses
from collections.abc import Mapping
from typing import Any, NotRequired, TypedDict

import httpx


class GraphQLResponseData(TypedDict):
    data: dict[str, Any]
    errors: NotRequired[Any]


@dataclasses.dataclass
class GraphQLResponse:
    response: httpx.Response
    data: GraphQLResponseData


class GraphQLClient:
    def __init__(self, client: httpx.AsyncClient, endpoint: str) -> None:
        self._client = client
        self._endpoint = endpoint

    async def query(
        self,
        query: str,
        variables: Mapping[str, Any] | None = None,
    ) -> GraphQLResponseData:
        return (await self.request(query=query, variables=variables)).data

    async def request(
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
        return GraphQLResponse(
            response=response,
            data=response.json(),
        )
