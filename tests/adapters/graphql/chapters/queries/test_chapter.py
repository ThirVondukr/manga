import uuid

import pytest

from app.db.models import MangaChapter
from tests.adapters.graphql.client import GraphQLClient

pytestmark = pytest.mark.usefixtures("session")

QUERY = """query ($id: ID!) {
  chapter(id: $id) {
    __typename
    id
    number
    title
    volume
  }
}"""


@pytest.mark.parametrize(
    "chapter_id",
    [
        str(uuid.uuid4()),
        "not-uuid",
    ],
)
async def test_not_found(
    graphql_client: GraphQLClient,
    chapter_id: str,
) -> None:
    response = await graphql_client.query(QUERY, variables={"id": chapter_id})
    assert response == {
        "data": {
            "chapter": None,
        },
    }


async def test_ok(
    graphql_client: GraphQLClient,
    manga_chapter: MangaChapter,
) -> None:
    response = await graphql_client.query(
        QUERY,
        variables={"id": str(manga_chapter.id)},
    )
    assert response == {
        "data": {
            "chapter": {
                "__typename": "MangaChapter",
                "id": str(manga_chapter.id),
                "title": manga_chapter.title,
                "volume": manga_chapter.volume,
                "number": ".".join(str(n) for n in manga_chapter.number),
            },
        },
    }
