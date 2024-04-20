from collections.abc import Sequence

from app.db.models.manga import MangaBookmark
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """query {
  myBookmarks {
    items {
      id
      status
      manga {
        id
      }
    }
  }
}
"""


def _tpl(bookmarks: Sequence[object]) -> object:
    return {
        "data": {
            "myBookmarks": {
                "items": bookmarks,
            },
        },
    }


async def test_requires_auth(graphql_client: GraphQLClient) -> None:
    response = await graphql_client.query(QUERY)
    assert_not_authenticated(response)


async def test_ok(
    user_bookmark_collection: Sequence[MangaBookmark],
    authenticated_graphql_client: GraphQLClient,
) -> None:
    response = await authenticated_graphql_client.query(QUERY)
    expected = [
        {
            "id": f"{bookmark.user_id}:{bookmark.manga_id}",
            "status": bookmark.status.name.upper(),
            "manga": {
                "id": str(bookmark.manga_id),
            },
        }
        for bookmark in sorted(
            user_bookmark_collection,
            key=lambda b: b.created_at,
            reverse=True,
        )
    ]
    assert response == _tpl(expected)
