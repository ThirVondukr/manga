import uuid

import pytest

from app.db.models import Manga
from tests.adapters.graphql.client import GraphQLClient

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("session")]

QUERY = """
query Query($id: ID!) {
    manga: manga(id: $id) {
        id
        title
        titleSlug
        createdAt
        updatedAt
    }
}
"""


def _tpl(manga: object) -> dict[str, object]:
    return {
        "data": {
            "manga": manga,
        },
    }


@pytest.mark.parametrize("manga_id", [str(uuid.uuid4()), "42"])
async def test_not_found(
    graphql_client: GraphQLClient,
    manga_id: str,
) -> None:
    response = await graphql_client.query(
        query=QUERY,
        variables={
            "id": manga_id,
        },
    )
    assert response == _tpl(None)


async def test_manga(
    manga: Manga,
    graphql_client: GraphQLClient,
) -> None:
    response = await graphql_client.query(
        query=QUERY,
        variables={"id": str(manga.id)},
    )
    assert response == _tpl(
        {
            "id": str(manga.id),
            "title": manga.title,
            "titleSlug": manga.title_slug,
            "createdAt": manga.created_at.isoformat(),
            "updatedAt": manga.updated_at.isoformat(),
        },
    )
