import uuid
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.bookmarks.commands import MangaBookmarkAddCommand
from app.core.domain.bookmarks.dto import BookmarkMangaResultDTO
from app.core.errors import NotFoundError
from app.db.models import Manga, MangaBookmark
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation($id: ID!) {
  manga {
    addBookmark(id: $id) {
      error {
        __typename
      }
      manga {
        __typename
        id
      }
    }
  }
}

"""


def _tpl(manga: object = None, error: object = None) -> object:
    return {
        "data": {
            "manga": {
                "addBookmark": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


async def test_requires_auth(graphql_client: GraphQLClient) -> None:
    response = await graphql_client.query(
        QUERY,
        variables={"id": str(uuid.uuid4())},
    )
    assert_not_authenticated(response)


@pytest.mark.parametrize(
    "manga_id",
    [
        "not-uuid",
        str(uuid.uuid4()),
    ],
)
async def test_not_found(
    authenticated_graphql_client: GraphQLClient,
    manga_id: str,
) -> None:
    with patch.object(
        MangaBookmarkAddCommand,
        MangaBookmarkAddCommand.execute.__name__,
        return_value=Err(NotFoundError(entity_id=manga_id)),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"id": manga_id},
        )
    assert response == _tpl(
        error={"__typename": "NotFoundError"},
    )


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    manga: Manga,
    manga_bookmark: MangaBookmark,
) -> None:
    with patch.object(
        MangaBookmarkAddCommand,
        MangaBookmarkAddCommand.execute.__name__,
        return_value=Ok(
            BookmarkMangaResultDTO(manga=manga, bookmark=manga_bookmark),
        ),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"id": str(manga.id)},
        )
    assert response == _tpl(
        manga={"__typename": "Manga", "id": str(manga.id)},
    )
