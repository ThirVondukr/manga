import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.auth.dto import TokenWrapper
from app.db.models import User
from tests.adapters.graphql.client import GraphQLClient

QUERY = """query {
  me {
    id
    username
  }
}
"""


@pytest.mark.parametrize(
    "user_exists",
    [True, False],
)
async def test_ok(
    user_exists: bool,
    session: AsyncSession,
    user: User,
    user_token: TokenWrapper,
    authenticated_graphql_client: GraphQLClient,
) -> None:
    if user_exists:
        user.username = str(uuid.uuid4())
        user.email = "new email"
        session.add(user)
        await session.flush()
    else:
        await session.flush()
        await session.delete(user)

    response = await authenticated_graphql_client.query(QUERY)
    assert response == {
        "data": {
            "me": {
                "id": str(user_token.claims.sub),
                "username": user_token.claims.preferred_username,
            },
        },
    }
    user = (
        await session.scalars(
            select(User).where(User.id == user_token.claims.sub),
        )
    ).one()

    assert user.username == user_token.claims.preferred_username
    assert user.email == user_token.claims.email
