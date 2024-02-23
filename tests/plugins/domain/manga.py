import random
from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Manga, MangaTag
from tests.factories import MangaFactory


@pytest.fixture
async def manga(session: AsyncSession) -> Manga:
    manga = MangaFactory.build()
    session.add(manga)
    await session.flush()
    return manga


@pytest.fixture
async def mangas(
    session: AsyncSession,
    tags: Sequence[MangaTag],
) -> Sequence[Manga]:
    mangas = MangaFactory.build_batch(size=50)
    for manga in mangas:
        manga.tags = list(random.sample(tags, k=3))

    session.add_all(mangas)
    await session.flush()
    return mangas
