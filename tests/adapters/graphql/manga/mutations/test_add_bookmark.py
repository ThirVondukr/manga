import uuid
from unittest.mock import patch

import pytest
from result import Err, Ok

from app.core.domain.manga.bookmarks.commands import MangaBookmarkAddCommand
from app.core.domain.manga.bookmarks.dto import BookmarkMangaResultDTO
from app.core.errors import NotFoundError
from app.db.models.manga import Manga, MangaBookmark
from tests.adapters.graphql.client import GraphQLClient
from tests.adapters.graphql.utils import assert_not_authenticated

QUERY = """mutation($input: MangaAddBookmarkInput!) {
  manga {
    addBookmark(input: $input) {
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
        variables={
            "input": {"mangaId": str(uuid.uuid4()), "status": "READING"},
        },
    )
    assert_not_authenticated(response)


@pytest.mark.parametrize(
    ("manga_id", "error_typename"),
    [
        ("not-uuid", "ValidationErrors"),
        (str(uuid.uuid4()), "NotFoundError"),
    ],
)
async def test_not_found(
    authenticated_graphql_client: GraphQLClient,
    manga_id: str,
    error_typename: str,
) -> None:
    with patch.object(
        MangaBookmarkAddCommand,
        MangaBookmarkAddCommand.execute.__name__,
        return_value=Err(NotFoundError(entity_id=manga_id)),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": {"mangaId": manga_id, "status": "READING"}},
        )
    assert response == _tpl(
        error={"__typename": error_typename},
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
            variables={
                "input": {"mangaId": str(manga.id), "status": "READING"},
            },
        )
    assert response == _tpl(
        manga={"__typename": "Manga", "id": str(manga.id)},
    )
