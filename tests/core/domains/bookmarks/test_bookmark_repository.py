import random
from collections.abc import Sequence

from app.core.domain.manga.bookmarks.repositories import BookmarkRepository
from app.core.domain.manga.manga.filters import (
    MangaBookmarkFilter,
    MangaBookmarkSortField,
    MangaFilter,
    Sort,
)
from app.db.models import User
from app.db.models.manga import MangaBookmark, MangaBookmarkStatus
from lib.pagination.pagination import PagePaginationParamsDTO
from lib.sort import SortDirection

_pagination = PagePaginationParamsDTO(
    page=1,
    page_size=100,
)
_sort = Sort(
    field=MangaBookmarkSortField.bookmark_added_at,
    direction=SortDirection.asc,
)


async def test_status_filter(
    bookmark_repository: BookmarkRepository,
    user: User,
    user_bookmark_collection: Sequence[MangaBookmark],
) -> None:
    status = random.choice(list(MangaBookmarkStatus.__members__.values()))
    expected = [b for b in user_bookmark_collection if b.status is status]
    expected.sort(key=lambda b: b.created_at)

    result = await bookmark_repository.user_bookmarks(
        user_id=user.id,
        pagination=_pagination,
        sort=_sort,
        filter=MangaBookmarkFilter(statuses=[status]),
    )
    assert result.items == expected


async def test_manga_filter(
    bookmark_repository: BookmarkRepository,
    user: User,
    user_bookmark_collection: Sequence[MangaBookmark],
) -> None:
    if not user_bookmark_collection:
        return

    bookmark = random.choice(user_bookmark_collection)
    result = await bookmark_repository.user_bookmarks(
        user_id=user.id,
        pagination=_pagination,
        sort=_sort,
        filter=MangaBookmarkFilter(
            manga=MangaFilter(search_term=bookmark.manga.title),
        ),
    )
    assert result.items == [bookmark]
