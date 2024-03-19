import uuid
from typing import Any
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.manga.art.command import MangaSetCoverArtCommand
from app.core.errors import PermissionDeniedError
from app.db.models.manga import Manga
from lib.db import DBContext
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated
from tests.factories import MangaArtFactory

QUERY = """mutation ($input: MangaSetCoverArtInput!) {
  manga {
    setCoverArt(input: $input) {
      manga {
        __typename
        id
        coverArt {
          __typename
          id
        }
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
                "setCoverArt": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def input(manga: Manga) -> dict[str, Any]:
    return {
        "mangaId": str(manga.id),
        "artId": str(uuid.uuid4()),
    }


async def test_requires_authentication(
    graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    response = await graphql_client.query(QUERY, variables={"input": input})
    assert_not_authenticated(response)


async def test_validation_error(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    input["mangaId"] = "42"
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    with patch.object(
        MangaSetCoverArtCommand,
        MangaSetCoverArtCommand.execute.__name__,
        return_value=Err(PermissionDeniedError()),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )
    assert response == _tpl(error={"__typename": "PermissionDeniedError"})


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
    manga: Manga,
    db_context: DBContext,
) -> None:
    cover_art = MangaArtFactory.build()
    manga.arts = [cover_art]
    await db_context.flush()
    manga.cover_art = cover_art
    assert manga.cover_art
    await db_context.flush()

    with patch.object(
        MangaSetCoverArtCommand,
        MangaSetCoverArtCommand.execute.__name__,
        return_value=Ok(manga),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )
    expected = {
        "__typename": "Manga",
        "id": str(manga.id),
        "coverArt": {
            "__typename": "MangaArt",
            "id": str(manga.cover_art.id),
        },
    }
    assert response == _tpl(manga=expected)
