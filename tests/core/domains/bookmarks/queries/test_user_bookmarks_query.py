from collections.abc import Sequence

import pytest

from app.core.domain.auth.dto import TokenWrapper
from app.core.domain.manga.bookmarks.queries import UserBookmarksQuery
from app.core.domain.manga.bookmarks.services import BookmarkService
from app.db.models import User
from app.db.models.manga import MangaBookmark, MangaBookmarkStatus
from lib.pagination.pagination import PagePaginationParamsDTO
from tests.factories import MangaFactory
from tests.types import Resolver
from tests.utils import casefold


@pytest.fixture
async def query(resolver: Resolver) -> UserBookmarksQuery:
    return await resolver(UserBookmarksQuery)


async def test_ok(
    query: UserBookmarksQuery,
    user_token: TokenWrapper,
    user_bookmark_collection: Sequence[MangaBookmark],
) -> None:
    result = await query.execute(
        user=user_token.claims,
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
    )
    assert result.items == sorted(
        user_bookmark_collection,
        key=lambda bookmark: casefold(bookmark.manga.title),
    )


async def test_other_user_bookmarks(
    collection_size: int,
    query: UserBookmarksQuery,
    bookmark_service: BookmarkService,
    user_token: TokenWrapper,
    other_user: User,
) -> None:
    mangas = MangaFactory.build_batch(size=collection_size)
    for manga in mangas:
        await bookmark_service.add_bookmark(
            user=other_user,
            manga=manga,
            status=MangaBookmarkStatus.reading,
        )

    result = await query.execute(
        user=user_token.claims,
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
    )
    assert result.items == []
