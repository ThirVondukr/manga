from app.db.models import Manga, MangaBranch, User
from lib.db import DBContext
from tests.adapters.graphql.client import GraphQLClient
from tests.factories import ChapterFactory

QUERY = """query ($mangaId: ID!) {
  manga(id: $mangaId) {
    id
    chapters {
      items {
        __typename
        id
        title
        volume
        number
      }
    }
  }
}"""


async def test_ok(
    graphql_client: GraphQLClient,
    manga: Manga,
    manga_branch: MangaBranch,
    db_context: DBContext,
    collection_size: int,
    chapter_factory: ChapterFactory,
    user: User,
) -> None:
    manga_branch.chapters = [
        chapter_factory(branch=manga_branch, created_by=user)
        for _ in range(collection_size)
    ]
    db_context.add(manga_branch)
    await db_context.flush()

    response = await graphql_client.query(
        QUERY,
        variables={"mangaId": str(manga.id)},
    )
    expected = {
        "id": str(manga.id),
        "chapters": {
            "items": [
                {
                    "__typename": "MangaChapter",
                    "id": str(chapter.id),
                    "title": chapter.title,
                    "volume": chapter.volume,
                    "number": ".".join(str(n) for n in chapter.number),
                }
                for chapter in reversed(manga_branch.chapters)
            ],
        },
    }
    assert response == {
        "data": {
            "manga": expected,
        },
    }
