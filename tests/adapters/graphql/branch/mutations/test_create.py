import uuid
from typing import Any
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.branches.commands import MangaBranchCreateCommand
from app.core.domain.const import GENERIC_NAME_LENGTH
from app.core.errors import RelationshipNotFoundError
from app.db.models import MangaBranch
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
        "groupId": str(uuid.uuid4()),
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


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (
            Err(
                RelationshipNotFoundError(
                    entity_name="Manga",
                    entity_id="not-found-id",
                ),
            ),
            {
                "__typename": "RelationshipNotFoundError",
                "entityId": "not-found-id",
            },
        ),
        (
            Err(
                RelationshipNotFoundError(
                    entity_name="Group",
                    entity_id="group-id",
                ),
            ),
            {
                "__typename": "RelationshipNotFoundError",
                "entityId": "group-id",
            },
        ),
    ],
)
async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
    result: Err[RelationshipNotFoundError],
    expected: object,
) -> None:
    with patch.object(MangaBranchCreateCommand, "execute", return_value=result):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )
        assert response == _tpl(
            error=expected,
        )


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
    manga_branch: MangaBranch,
) -> None:
    with patch.object(
        MangaBranchCreateCommand,
        "execute",
        return_value=Ok(manga_branch),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )

    assert response == _tpl(
        branch={
            "__typename": "MangaBranch",
            "id": str(manga_branch.id),
            "name": manga_branch.name,
            "language": manga_branch.language.name.upper(),
        },
    )
