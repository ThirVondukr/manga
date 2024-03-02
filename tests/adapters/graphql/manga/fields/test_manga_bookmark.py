from app.db.models import Manga, MangaBookmark
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """query ($id: ID!) {
  manga(id: $id) {
    id
    bookmark {
      __typename
      id
      createdAt
    }
  }
}"""


async def test_requires_auth(
    graphql_client: GraphQLClient,
    manga: Manga,
) -> None:
    response = await graphql_client.query(
        QUERY,
        variables={"id": str(manga.id)},
    )
    assert_not_authenticated(response)


async def test_no_bookmark(
    manga: Manga,
    authenticated_graphql_client: GraphQLClient,
) -> None:
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"id": str(manga.id)},
    )
    assert response == {
        "data": {
            "manga": {
                "id": str(manga.id),
                "bookmark": None,
            },
        },
    }


async def test_ok(
    manga: Manga,
    manga_bookmark: MangaBookmark,
    authenticated_graphql_client: GraphQLClient,
) -> None:
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"id": str(manga.id)},
    )
    assert response == {
        "data": {
            "manga": {
                "id": str(manga.id),
                "bookmark": {
                    "__typename": "MangaBookmark",
                    "id": f"{manga_bookmark.manga_id}:{manga_bookmark.user_id}",
                    "createdAt": manga_bookmark.created_at.isoformat(),
                },
            },
        },
    }
