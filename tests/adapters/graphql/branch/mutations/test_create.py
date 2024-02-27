import uuid
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.const import GENERIC_NAME_LENGTH
from app.db.models import Manga, MangaBranch
from lib.types import Language
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation ($input: MangaBranchCreateInput!) {
  branches {
    create(input: $input) {
      branch {
        __typename
        id
        name
        language
      }
      error {
        __typename
        ... on RelationshipNotFoundError {
            entityId
        }
      }
    }
  }
}

"""


def _tpl(
    branch: object | None = None,
    error: object | None = None,
) -> object:
    return {
        "data": {
            "branches": {
                "create": {
                    "branch": branch,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def input(language: Language) -> dict[str, Any]:
    return {
        "name": str(uuid.uuid4()),
        "language": language.name.upper(),
        "mangaId": str(uuid.uuid4()),
    }


async def test_requires_auth(
    graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    response = await graphql_client.query(QUERY, variables={"input": input})
    assert_not_authenticated(response)


async def test_validation_err(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    input["name"] = "a" * (GENERIC_NAME_LENGTH + 1)
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_manga_not_found(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
    )
    assert response == _tpl(
        error={
            "__typename": "RelationshipNotFoundError",
            "entityId": input["mangaId"],
        },
    )


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
    manga: Manga,
    session: AsyncSession,
) -> None:
    input["mangaId"] = str(manga.id)
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
    )

    branch = (await session.scalars(select(MangaBranch))).one()
    assert branch.manga is manga
    assert branch.name == input["name"]
    assert branch.language.name.upper() == input["language"]

    assert response == _tpl(
        branch={
            "__typename": "MangaBranch",
            "id": str(branch.id),
            "name": branch.name,
            "language": branch.language.name.upper(),
        },
    )
