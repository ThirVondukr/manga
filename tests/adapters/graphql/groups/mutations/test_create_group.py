import uuid
from uuid import UUID

from app.core.domain.const import GENERIC_NAME_LENGTH
from app.core.domain.groups.repositories import GroupRepository
from app.db.models import Group
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation ($input: GroupCreateInput!) {
  groups {
    create(input: $input) {
      __typename
      error {
        __typename
      }
      group {
        __typename
        id
        name
      }
    }
  }
}

"""


def _tpl(error: object = None, group: object = None) -> object:
    return {
        "data": {
            "groups": {
                "create": {
                    "__typename": "GroupCreatePayload",
                    "error": error,
                    "group": group,
                },
            },
        },
    }


async def test_requires_auth(graphql_client: GraphQLClient) -> None:
    response = await graphql_client.query(
        query=QUERY,
        variables={"input": {"name": "Group Name"}},
    )
    assert_not_authenticated(response)


async def test_validation_error(
    authenticated_graphql_client: GraphQLClient,
) -> None:
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={"input": {"name": "A" * (GENERIC_NAME_LENGTH + 1)}},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_already_exists(
    authenticated_graphql_client: GraphQLClient,
    group: Group,
) -> None:
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={"input": {"name": group.name}},
    )
    assert response == _tpl(error={"__typename": "EntityAlreadyExistsError"})


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    group_repository: GroupRepository,
) -> None:
    name = str(uuid.uuid4())
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={"input": {"name": name}},
    )
    group = await group_repository.get(
        id=UUID(response["data"]["groups"]["create"]["group"]["id"]),
    )
    assert group
    assert response == _tpl(
        group={
            "__typename": "Group",
            "id": str(group.id),
            "name": name,
        },
    )
