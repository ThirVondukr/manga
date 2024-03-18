import random
import uuid

import pytest

from app.db.models import Manga, User
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation ($input: MangaSetRatingInput!) {
  manga {
    setRating(input: $input) {
      manga {
        id
        rating
        ratingCount
      }
      rating {
        id
        value
      }
      error {
        __typename
      }
    }
  }
}
"""


def _tpl(
    manga: object = None,
    rating: object = None,
    error: object = None,
) -> object:
    return {
        "data": {
            "manga": {
                "setRating": {
                    "manga": manga,
                    "rating": rating,
                    "error": error,
                },
            },
        },
    }


async def test_requires_authentication(graphql_client: GraphQLClient) -> None:
    response = await graphql_client.query(
        QUERY,
        variables={"input": {"mangaId": str(uuid.uuid4()), "rating": 5}},
    )
    assert_not_authenticated(response)


@pytest.mark.parametrize("rating", [-1, 0, 11])
async def test_validation_error(
    rating: int,
    authenticated_graphql_client: GraphQLClient,
) -> None:
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": {"mangaId": str(uuid.uuid4()), "rating": rating}},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_err(authenticated_graphql_client: GraphQLClient) -> None:
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": {"mangaId": str(uuid.uuid4()), "rating": 10}},
    )
    assert response == _tpl(error={"__typename": "NotFoundError"})


async def test_ok(
    manga: Manga,
    authenticated_graphql_client: GraphQLClient,
    user: User,
) -> None:
    rating = random.randint(1, 10)
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": {"mangaId": str(manga.id), "rating": rating}},
    )
    assert response == _tpl(
        manga={"id": str(manga.id), "rating": rating, "ratingCount": 1},
        rating={
            "id": f"{manga.id}:{user.id}",
            "value": rating,
        },
    )
