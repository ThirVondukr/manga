import random

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga
from lib.types import MangaStatus
from tests.adapters.graphql.client import GraphQLClient

pytestmark = [pytest.mark.usefixtures("session")]

QUERY = """mutation Mutation($input: MangaCreateInput!) {
  manga {
    create(input: $input) {
      manga {
        id
        title
        titleSlug
      }
      error {
        __typename
      }
    }
  }
}
"""


def _tpl(manga: object, error: object) -> object:
    return {
        "data": {
            "manga": {
                "create": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def manga_status() -> MangaStatus:
    return random.choice(list(MangaStatus.__members__.values()))


async def test_validation(
    graphql_client: GraphQLClient,
    manga_status: MangaStatus,
) -> None:
    title = "a" * 251
    response = await graphql_client.query(
        query=QUERY,
        variables={
            "input": {"title": title, "status": manga_status.name.upper()},
        },
    )
    assert response == _tpl(
        manga=None,
        error={"__typename": "ValidationErrors"},
    )


async def test_create(
    session: AsyncSession,
    graphql_client: GraphQLClient,
    manga_status: MangaStatus,
) -> None:
    title = "Test Manga Title"
    response = await graphql_client.query(
        query=QUERY,
        variables={
            "input": {"title": title, "status": manga_status.name.upper()},
        },
    )

    manga = await session.scalar(select(Manga))
    assert manga
    assert response == _tpl(
        manga={
            "id": str(manga.id),
            "title": title,
            "titleSlug": "test-manga-title",
        },
        error=None,
    )
