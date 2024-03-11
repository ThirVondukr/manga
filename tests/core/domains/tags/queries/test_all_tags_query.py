import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.tags.query import AllMangaTagsQuery
from tests.factories import MangaTagFactory
from tests.types import Resolver
from tests.utils import casefold


@pytest.fixture
async def query(resolver: Resolver) -> AllMangaTagsQuery:
    return await resolver(AllMangaTagsQuery)


async def test_ok(
    session: AsyncSession,
    collection_size: int,
    query: AllMangaTagsQuery,
) -> None:
    tags = MangaTagFactory.build_batch(size=collection_size)
    tags.sort(key=lambda tag: casefold(tag.name))
    session.add_all(tags)
    await session.flush()

    result = await query.execute()
    assert result == tags
