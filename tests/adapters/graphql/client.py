import dataclasses
import json
import mimetypes
import uuid
from collections.abc import Mapping, MutableMapping, Sequence
from io import BytesIO
from typing import Any, NotRequired, TypedDict

import httpx


class GraphQLResponseData(TypedDict):
    data: dict[str, Any]
    errors: NotRequired[Any]


@dataclasses.dataclass
class GraphQLResponse:
    response: httpx.Response
    data: GraphQLResponseData


@dataclasses.dataclass(kw_only=True)
class GraphQLFile:
    buffer: BytesIO
    name: str
    content_type: str | None = None
    content_type_: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        if self.content_type is None:
            self.content_type, _ = mimetypes.guess_type(url=self.name)
        self.content_type_ = self.content_type  # type: ignore[assignment]


def _create_file_mapping(
    *,
    files: Mapping[str, Sequence[GraphQLFile] | GraphQLFile] | None = None,
    placeholder: str,
) -> tuple[
    Mapping[str, list[str]],
    Mapping[str, tuple[str, BytesIO, str]],
]:
    files = files or {}
    file_ids = {}
    file_mappings = {}

    for key, file_list in files.items():
        if isinstance(file_list, GraphQLFile):
            id_ = str(uuid.uuid4())
            file_key = f"variables.{key}"
            file_ids[id_] = [file_key]
            file_mappings[id_] = (
                file_list.name,
                file_list.buffer,
                file_list.content_type_,
            )

        else:
            for i, file in enumerate(file_list):
                id_ = str(uuid.uuid4())
                if placeholder in key:
                    file_key = f"variables.{key.replace(placeholder, str(i))}"
                else:
                    file_key = f"variables.{key}.{i}"

                file_ids[id_] = [file_key]
                file_mappings[id_] = (
                    file.name,
                    file.buffer,
                    file.content_type_,
                )

    return file_ids, file_mappings


class GraphQLClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        file_map_placeholder: str = "$",
    ) -> None:
        self._client = client
        self._endpoint = endpoint
        self._file_map_placeholder = file_map_placeholder

    async def query(
        self,
        query: str,
        variables: MutableMapping[str, Any] | None = None,
        files: Mapping[str, Sequence[GraphQLFile] | GraphQLFile] | None = None,
    ) -> GraphQLResponseData:
        return (
            await self.request(query=query, variables=variables, files=files)
        ).data

    async def request(
        self,
        query: str,
        variables: MutableMapping[str, Any] | None = None,
        files: Mapping[str, Sequence[GraphQLFile] | GraphQLFile] | None = None,
    ) -> GraphQLResponse:
        variables = variables or {}
        files = files or {}
        file_ids, file_mappings = _create_file_mapping(
            files=files,
            placeholder=self._file_map_placeholder,
        )

        for key, file_list in files.items():
            if isinstance(file_list, list):
                variables[key] = [None] * len(file_list)
            else:
                variables[key] = None

        response = await self._client.post(
            self._endpoint,
            files={
                "operations": (
                    None,
                    json.dumps(
                        {
                            "query": query,
                            "variables": variables,
                        },
                    ),
                ),
                "map": (None, json.dumps(file_ids)),
                **file_mappings,
            },
        )
        response.raise_for_status()
        return GraphQLResponse(
            response=response,
            data=response.json(),
        )
