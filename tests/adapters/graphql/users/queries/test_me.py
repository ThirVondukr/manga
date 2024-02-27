from app.db.models import User
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """query {
  me {
    __typename
    id
    username
    joinedAt
    email
  }
}
"""


async def test_requires_auth(graphql_client: GraphQLClient) -> None:
    response = await graphql_client.query(QUERY)
    assert_not_authenticated(response)


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    user: User,
) -> None:
    response = await authenticated_graphql_client.query(QUERY)
    assert response == {
        "data": {
            "me": {
                "__typename": "PrivateUser",
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "joinedAt": user.created_at.isoformat(),
            },
        },
    }
