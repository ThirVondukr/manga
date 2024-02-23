from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MangaTag
from tests.factories import MangaTagFactory


@pytest.fixture
async def tags(session: AsyncSession) -> Sequence[MangaTag]:
    tags = MangaTagFactory.build_batch(size=10)
    session.add_all(tags)
    await session.flush()
    return tags
