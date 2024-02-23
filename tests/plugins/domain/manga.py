import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga
from tests.factories import MangaFactory


@pytest.fixture
async def manga(session: AsyncSession) -> Manga:
    manga = MangaFactory.build()
    session.add(manga)
    await session.flush()
    return manga
