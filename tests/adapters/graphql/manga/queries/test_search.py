import math
import random
from collections.abc import Sequence

import pytest

from app.db.models import Manga
from tests.adapters.graphql.client import GraphQLClient

pytestmark = [pytest.mark.usefixtures("session")]

QUERY = """
query SearchManga($filter: MangaFilter! = {}, $pagination: PagePaginationInput! = {}) {
    mangas(filter: $filter, pagination: $pagination) {
        pageInfo {
            currentPage
            hasNextPage
            hasPreviousPage
            pageSize
            totalItems
            totalPages
        }
        items {
            id
        }
    }
}
"""


def _tpl(mangas: object) -> object:
    return {
        "data": {
            "mangas": mangas,
        },
    }


async def test_search(
    graphql_client: GraphQLClient,
    mangas: Sequence[Manga],
) -> None:
    total_items = len(mangas)
    page_size = 9

    mangas = sorted(mangas, key=lambda m: m.created_at, reverse=True)
    total_pages = math.ceil(total_items / page_size)

    for page in range(1, total_pages + 1):
        response = await graphql_client.query(
            query=QUERY,
            variables={
                "pagination": {
                    "pageSize": page_size,
                    "page": page,
                },
            },
        )
        assert response == _tpl(
            {
                "pageInfo": {
                    "currentPage": page,
                    "hasNextPage": page < total_pages,
                    "hasPreviousPage": page > 1,
                    "pageSize": page_size,
                    "totalItems": len(mangas),
                    "totalPages": total_pages,
                },
                "items": [
                    {"id": str(manga.id)}
                    for manga in mangas[
                        (page - 1) * page_size : page * page_size
                    ]
                ],
            },
        )


async def test_tags_search(
    graphql_client: GraphQLClient,
    mangas: Sequence[Manga],
) -> None:
    manga_with_tags = next(m for m in mangas if m.tags)
    random_tag = random.choice(manga_with_tags.tags)
    expected = [m for m in mangas if random_tag in m.tags]
    expected.sort(key=lambda m: m.created_at, reverse=True)
    response = await graphql_client.query(
        query=QUERY,
        variables={
            "pagination": {
                "pageSize": len(mangas),
            },
            "filter": {"tags": {"include": [random_tag.name_slug]}},
        },
    )
    assert response == _tpl(
        {
            "pageInfo": {
                "currentPage": 1,
                "hasNextPage": False,
                "hasPreviousPage": False,
                "pageSize": len(mangas),
                "totalItems": len(expected),
                "totalPages": 1,
            },
            "items": [{"id": str(manga.id)} for manga in expected],
        },
    )
