from collections.abc import Sequence
from unittest.mock import patch

from app.core.domain.manga.tags.query import AllMangaTagsQuery
from app.db.models.manga import MangaTag
from tests.adapters.graphql.client import GraphQLClient
from tests.utils import casefold

QUERY = """query {
  tags {
    __typename
    id
    name
    slug
  }
}
"""


async def test_ok(
    tags: Sequence[MangaTag],
    graphql_client: GraphQLClient,
) -> None:
    tags = sorted(tags, key=lambda tag: casefold(tag.name))
    with patch.object(AllMangaTagsQuery, "execute", return_value=tags):
        response = await graphql_client.query(QUERY)

    assert response == {
        "data": {
            "tags": [
                {
                    "__typename": "MangaTag",
                    "id": str(tag.id),
                    "name": tag.name,
                    "slug": tag.name_slug,
                }
                for tag in tags
            ],
        },
    }
