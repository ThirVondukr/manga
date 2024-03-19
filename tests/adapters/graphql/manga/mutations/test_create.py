import uuid
from typing import Any
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.manga.manga.commands import MangaCreateCommand
from app.core.errors import EntityAlreadyExistsError
from app.db.models.manga import Manga
from lib.types import MangaStatus
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

pytestmark = [pytest.mark.usefixtures("session")]

QUERY = """mutation Mutation($input: MangaCreateInput!) {
  manga {
    create(input: $input) {
      manga {
        id
        title
        titleSlug
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
                "create": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def input(manga_status: MangaStatus) -> dict[str, Any]:
    return {
        "title": str(uuid.uuid4()),
        "description": str(uuid.uuid4()),
        "status": manga_status.name.upper(),
    }


async def test_requires_auth(
    graphql_client: GraphQLClient,
    input: object,
) -> None:
    response = await graphql_client.query(
        query=QUERY,
        variables={
            "input": input,
        },
    )
    assert_not_authenticated(response)


async def test_validation(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    input["title"] = "a" * 251
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={
            "input": input,
        },
    )
    assert response == _tpl(
        manga=None,
        error={"__typename": "ValidationErrors"},
    )


@pytest.mark.parametrize(
    ("typename", "err"),
    [
        ("EntityAlreadyExistsError", EntityAlreadyExistsError()),
    ],
)
async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: object,
    typename: str,
    err: object,
) -> None:
    with patch.object(MangaCreateCommand, "execute", return_value=Err(err)):
        response = await authenticated_graphql_client.query(
            query=QUERY,
            variables={
                "input": input,
            },
        )

    assert response == _tpl(
        error={
            "__typename": typename,
        },
    )


async def test_create(
    authenticated_graphql_client: GraphQLClient,
    manga: Manga,
    input: object,
) -> None:
    with patch.object(MangaCreateCommand, "execute", return_value=Ok(manga)):
        response = await authenticated_graphql_client.query(
            query=QUERY,
            variables={
                "input": input,
            },
        )

    assert response == _tpl(
        manga={
            "id": str(manga.id),
            "title": manga.title,
            "titleSlug": manga.title_slug,
        },
        error=None,
    )
