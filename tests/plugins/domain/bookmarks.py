import pytest

from app.core.domain.bookmarks.repositories import BookmarkRepository
from app.core.domain.bookmarks.services import BookmarkService
from app.db.models import Manga, MangaBookmark, User
from tests.types import Resolver


@pytest.fixture
async def bookmark_repository(resolver: Resolver) -> BookmarkRepository:
    return await resolver(BookmarkRepository)


@pytest.fixture
async def bookmark_service(resolver: Resolver) -> BookmarkService:
    return await resolver(BookmarkService)


@pytest.fixture
async def manga_bookmark(
    bookmark_service: BookmarkService,
    manga: Manga,
    user: User,
) -> MangaBookmark:
    return await bookmark_service.bookmark(manga=manga, user=user)
