from collections.abc import Sequence

import pytest

from app.core.domain.manga.bookmarks.repositories import BookmarkRepository
from app.core.domain.manga.bookmarks.services import BookmarkService
from app.db.models import User
from app.db.models.manga import Manga, MangaBookmark, MangaBookmarkStatus
from tests.factories import MangaFactory
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
    return await bookmark_service.add_bookmark(
        manga=manga,
        user=user,
        status=MangaBookmarkStatus.reading,
    )


@pytest.fixture
async def user_bookmark_collection(
    collection_size: int,
    user: User,
    bookmark_service: BookmarkService,
) -> Sequence[MangaBookmark]:
    mangas = MangaFactory.build_batch(size=collection_size)
    return [
        await bookmark_service.add_bookmark(
            user=user,
            manga=manga,
            status=MangaBookmarkStatus.reading,
        )
        for manga in mangas
    ]
