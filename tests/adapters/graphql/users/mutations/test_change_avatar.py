from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ImageSet, User
from tests.adapters.graphql.client import GraphQLClient, GraphQLFile
from tests.adapters.graphql.utils import assert_not_authenticated
from tests.utils import create_dummy_image

MUTATION = """mutation ($avatar: Upload!) {
  user {
    changeAvatar(avatar: $avatar) {
      user {
        id
        avatar {
          id
        }
      }
      error {
        __typename
      }
    }
  }
}"""


async def test_requires_auth(graphql_client: GraphQLClient) -> None:
    image = create_dummy_image()
    response = await graphql_client.query(
        MUTATION,
        files={"avatar": GraphQLFile(name="avatar.png", buffer=image)},
    )
    assert_not_authenticated(response)


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    user: User,
    session: AsyncSession,
) -> None:
    image = create_dummy_image()
    response = await authenticated_graphql_client.query(
        MUTATION,
        files={"avatar": GraphQLFile(name="avatar.png", buffer=image)},
    )
    avatar = (await session.scalars(select(ImageSet))).one()
    assert response == {
        "data": {
            "user": {
                "changeAvatar": {
                    "user": {
                        "id": str(user.id),
                        "avatar": {
                            "id": str(avatar.id),
                        },
                    },
                    "error": None,
                },
            },
        },
    }
