from typing import Any

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from tests.graphql.client import GraphQLClient

pytestmark = pytest.mark.anyio

_QUERY = """mutation ($input: UserRegisterInput!) {
  users {
    register(input: $input) {
      user {
        id
        username
      }
      error {
        __typename
      }
    }
  }
}
"""


@pytest.fixture
def input(faker: Faker) -> dict[str, str]:
    return {
        "username": faker.pystr(),
        "email": faker.email(),
        "password": "pass",
    }


def _tpl(
    error: dict[str, str] | None = None,
    user: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "data": {
            "users": {
                "register": {
                    "error": error,
                    "user": user,
                },
            },
        },
    }


async def test_ok(
    graphql_client: GraphQLClient,
    input: dict[str, str],
    session: AsyncSession,
) -> None:
    response = await graphql_client.query(_QUERY, {"input": input})
    new_user = (await session.scalars(select(User))).one()
    assert response == _tpl(
        user={
            "id": str(new_user.id),
            "username": new_user.username,
        },
    )


async def test_validation_err(
    graphql_client: GraphQLClient,
    input: dict[str, str],
) -> None:
    input["email"] = "That's not really an email"
    response = await graphql_client.query(_QUERY, {"input": input})
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_user_already_exists(
    graphql_client: GraphQLClient,
    input: dict[str, str],
    user: User,
) -> None:
    input["email"] = user.email
    response = await graphql_client.query(_QUERY, {"input": input})
    assert response == _tpl(error={"__typename": "EntityAlreadyExistsError"})
