import uuid
from pathlib import PurePath

from app.core.storage import FileStorage
from app.db.models import Image
from app.db.models.manga import MangaChapter, MangaPage
from lib.db import DBContext
from tests.adapters.graphql.client import GraphQLClient

QUERY = """query ($id: ID!) {
  chapter(id: $id) {
    id
    pages {
      __typename
      id
      number
      images {
        url
        width
        height
      }
    }
  }
}"""


async def test_ok(
    graphql_client: GraphQLClient,
    manga_chapter: MangaChapter,
    collection_size: int,
    db_context: DBContext,
    image_storage: FileStorage,
) -> None:
    pages = [
        MangaPage(
            number=i,
            chapter=manga_chapter,
            images=[
                Image(
                    path=PurePath(f"{uuid.uuid4()}.png"),
                    width=1000,
                    height=1800,
                ),
            ],
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
                        "images": [
                            {
                                "url": await image_storage.url(str(image.path)),
                                "width": image.width,
                                "height": image.height,
                            }
                            for image in page.images
                        ],
                    }
                    for page in pages
                ],
            },
        },
    }
