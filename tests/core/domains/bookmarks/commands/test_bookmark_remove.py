import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.bookmarks.commands import (
    MangaBookmarkRemoveCommand,
)
from app.core.errors import NotFoundError
from app.db.models import Manga, MangaBookmark, User
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaBookmarkRemoveCommand:
    return await resolver(MangaBookmarkRemoveCommand)


async def test_manga_not_found(
    command: MangaBookmarkRemoveCommand,
    user: User,
) -> None:
    manga_id = uuid.uuid4()
    result = await command.execute(manga_id=manga_id, user=user)
    assert result.unwrap_err() == NotFoundError(entity_id=str(manga_id))


async def test_no_bookmark(
    command: MangaBookmarkRemoveCommand,
    user: User,
    manga: Manga,
) -> None:
    await command.execute(user=user, manga_id=manga.id)


@pytest.mark.usefixtures("manga_bookmark")
async def test_ok(
    command: MangaBookmarkRemoveCommand,
    user: User,
    manga: Manga,
    session: AsyncSession,
) -> None:
    assert manga.bookmark_count == 1
    (await command.execute(manga_id=manga.id, user=user)).unwrap()
    bookmarks = (await session.scalars(select(MangaBookmark))).all()
    assert bookmarks == []
    assert manga.bookmark_count == 0
