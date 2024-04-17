import random
from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.manga import Manga, MangaTag
from lib.db import DBContext
from lib.types import MangaStatus
from tests.factories import MangaFactory


@pytest.fixture
async def manga(session: AsyncSession, db_context: DBContext) -> Manga:
    manga = MangaFactory.build()
    session.add(manga)
    db_context.add(manga)
    await db_context.flush()
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
    return mangas


@pytest.fixture
def manga_status() -> MangaStatus:
    return random.choice(list(MangaStatus.__members__.values()))
