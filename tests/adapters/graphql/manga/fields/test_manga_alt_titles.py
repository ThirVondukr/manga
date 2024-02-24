from app.db.models import Manga
from lib.db import DBContext
from tests.adapters.graphql.client import GraphQLClient
from tests.factories import MangaAltTitleFactory

_QUERY = """query ($id: ID!) {
  manga(id: $id) {
    id
    altTitles {
      __typename
      id
      language
      title
    }
  }
}
"""


def _tpl(manga: object) -> object:
    return {
        "data": {
            "manga": manga,
        },
    }


async def test_ok(
    manga: Manga,
    graphql_client: GraphQLClient,
    collection_size: int,
    db_context: DBContext,
) -> None:
    manga.alt_titles = MangaAltTitleFactory.build_batch(size=collection_size)
    manga.alt_titles.sort(
        key=lambda alt_title: (alt_title.language.name, alt_title.id),
    )
    db_context.add(manga)
    await db_context.flush()

    response = await graphql_client.query(
        query=_QUERY,
        variables={"id": str(manga.id)},
    )
    assert response == _tpl(
        {
            "id": str(manga.id),
            "altTitles": [
                {
                    "__typename": "AltTitle",
                    "id": str(alt_title.id),
                    "language": alt_title.language.name,
                    "title": alt_title.title,
                }
                for alt_title in manga.alt_titles
            ],
        },
    )
