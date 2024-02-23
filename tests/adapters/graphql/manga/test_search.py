import math
import operator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.adapters.graphql.client import GraphQLClient
from tests.factories import MangaFactory

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("session")]

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
    session: AsyncSession,
) -> None:
    total_items = 50
    page_size = 9

    manga_list = MangaFactory.build_batch(size=total_items)
    session.add_all(manga_list)
    await session.flush()
    manga_list.sort(key=operator.attrgetter("created_at"), reverse=True)

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
                    "totalItems": len(manga_list),
                    "totalPages": total_pages,
                },
                "items": [
                    {"id": str(manga.id)}
                    for manga in manga_list[
                        (page - 1) * page_size : page * page_size
                    ]
                ],
            },
        )
