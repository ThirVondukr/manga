import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga
from tests.adapters.graphql.client import GraphQLClient
from tests.factories import MangaTagFactory

pytestmark = pytest.mark.anyio

_QUERY = """query ($id: ID!) {
  manga(id: $id) {
    id
    tags {
      __typename
      id
      name
      slug
    }
  }
}
"""


def _tpl(manga: object) -> object:
    return {
        "data": {"manga": manga},
    }


async def test_ok(
    collection_size: int,
    session: AsyncSession,
    manga: Manga,
    graphql_client: GraphQLClient,
) -> None:
    manga.tags = MangaTagFactory.build_batch(size=collection_size)
    manga.tags.sort(key=lambda tag: tag.name_slug)
    session.add(manga)
    await session.flush()

    response = await graphql_client.query(
        query=_QUERY,
        variables={"id": str(manga.id)},
    )
    assert response == _tpl(
        {
            "id": str(manga.id),
            "tags": [
                {
                    "__typename": "MangaTag",
                    "id": str(tag.id),
                    "name": tag.name,
                    "slug": tag.name_slug,
                }
                for tag in manga.tags
            ],
        },
    )
