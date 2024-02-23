from typing import Any

import pytest

from app.db.models import User
from app.settings import AuthSettings
from tests.adapters.graphql.client import GraphQLClient

pytestmark = pytest.mark.anyio

_QUERY = """mutation ($input: SignInInput!) {
  auth {
    signIn(input: $input) {
      result {
        user {
          id
          username
        }
      }
      error {
        __typename
      }
    }
  }
}
"""


def _tpl(
    error: dict[str, object] | None = None,
    result: dict[str, object] | None = None,
) -> dict[str, Any]:
    return {
        "data": {
            "auth": {
                "signIn": {
                    "error": error,
                    "result": result,
                },
            },
        },
    }


async def test_ok(
    graphql_client: GraphQLClient,
    auth_settings: AuthSettings,
    user: User,
    user_password: str,
) -> None:
    response = await graphql_client.request(
        _QUERY,
        {
            "input": {
                "email": user.email,
                "password": user_password,
            },
        },
    )
    assert response.data == _tpl(
        result={
            "user": {
                "id": str(user.id),
                "username": user.username,
            },
        },
    )
    assert auth_settings.refresh_token_cookie in response.response.cookies


async def test_invalid_password(
    graphql_client: GraphQLClient,
    auth_settings: AuthSettings,
    user: User,
) -> None:
    response = await graphql_client.request(
        _QUERY,
        {
            "input": {
                "email": user.email,
                "password": "user_password",
            },
        },
    )
    assert response.data == _tpl(
        result=None,
        error={"__typename": "InvalidCredentialsError"},
    )
    assert auth_settings.refresh_token_cookie not in response.response.cookies
