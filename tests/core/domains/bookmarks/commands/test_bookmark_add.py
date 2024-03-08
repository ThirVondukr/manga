import uuid

import pytest

from app.core.domain.bookmarks.commands import MangaBookmarkAddCommand
from app.core.domain.bookmarks.repositories import BookmarkRepository
from app.core.errors import NotFoundError
from app.db.models import Manga, User
from tests.types import Resolver


@pytest.fixture
async def command(resolver: Resolver) -> MangaBookmarkAddCommand:
    return await resolver(MangaBookmarkAddCommand)


async def test_manga_not_found(
    command: MangaBookmarkAddCommand,
    user: User,
) -> None:
    manga_id = uuid.uuid4()
    result = await command.execute(manga_id=manga_id, user=user)
    assert result.unwrap_err() == NotFoundError(entity_id=str(manga_id))


async def test_already_exists(
    command: MangaBookmarkAddCommand,
    user: User,
    manga: Manga,
) -> None:
    bookmark1 = (await command.execute(manga_id=manga.id, user=user)).unwrap()
    bookmark2 = (await command.execute(manga_id=manga.id, user=user)).unwrap()

    assert bookmark1.bookmark is bookmark2.bookmark


async def test_ok(
    command: MangaBookmarkAddCommand,
    user: User,
    manga: Manga,
    bookmark_repository: BookmarkRepository,
) -> None:
    result = (await command.execute(manga_id=manga.id, user=user)).unwrap()

    assert (
        await bookmark_repository.get(manga=manga, user=user) == result.bookmark
    )
    assert result.bookmark.manga == manga
    assert result.bookmark.user == user
    assert result.manga is manga