import uuid

from app.core.storage import ImageStorage
from app.db.models import MangaChapter, MangaPage
from lib.db import DBContext
from tests.adapters.graphql.client import GraphQLClient

QUERY = """query ($id: ID!) {
  chapter(id: $id) {
    id
    pages {
      __typename
      id
      number
      image
    }
  }
}"""


async def test_ok(
    graphql_client: GraphQLClient,
    manga_chapter: MangaChapter,
    collection_size: int,
    db_context: DBContext,
    image_storage: ImageStorage,
) -> None:
    pages = [
        MangaPage(
            number=i,
            image_path=f"{uuid.uuid4()}.jpg",
            chapter=manga_chapter,
        )
        for i in range(collection_size)
    ]
    manga_chapter.pages = pages
    db_context.add(manga_chapter)

    response = await graphql_client.query(
        QUERY,
        variables={"id": str(manga_chapter.id)},
    )
    assert response == {
        "data": {
            "chapter": {
                "id": str(manga_chapter.id),
                "pages": [
                    {
                        "__typename": "MangaPage",
                        "id": str(page.id),
                        "number": page.number,
                        "image": await image_storage.url(page.image_path),
                    }
                    for page in pages
                ],
            },
        },
    }
