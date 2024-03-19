import uuid
from typing import Any
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.const import NAME_LENGTH
from app.core.domain.manga.manga.commands import MangaUpdateCommand
from app.core.errors import NotFoundError
from app.db.models.manga import Manga
from lib.types import MangaStatus
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation MangaUpdate($input: MangaUpdateInput!) {
  manga {
    update(input: $input) {
      manga {
        __typename
        id
        title
        titleSlug
        status
      }
      error {
        __typename
      }
    }
  }
}

"""


def _tpl(manga: object = None, error: object = None) -> object:
    return {
        "data": {
            "manga": {
                "update": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def input(manga_status: MangaStatus, manga: Manga) -> dict[str, Any]:
    return {
        "id": str(manga.id),
        "title": str(uuid.uuid4()),
        "description": str(uuid.uuid4()),
        "status": manga_status.name.upper(),
    }


async def test_requires_authentication(
    graphql_client: GraphQLClient,
    input: object,
) -> None:
    result = await graphql_client.query(QUERY, variables={"input": input})
    assert_not_authenticated(result)


async def test_validation_error(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    input["title"] = NAME_LENGTH * "a" + "a"
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: object,
) -> None:
    with patch.object(
        MangaUpdateCommand,
        MangaUpdateCommand.execute.__name__,
        return_value=Err(NotFoundError(entity_id="")),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )

    assert response == _tpl(error={"__typename": "NotFoundError"})


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: object,
    manga: Manga,
) -> None:
    with patch.object(
        MangaUpdateCommand,
        MangaUpdateCommand.execute.__name__,
        return_value=Ok(manga),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )
    assert response == _tpl(
        manga={
            "__typename": "Manga",
            "id": str(manga.id),
            "title": manga.title,
            "titleSlug": manga.title_slug,
            "status": manga.status.name.upper(),
        },
    )
