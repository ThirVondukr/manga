import pytest

from app.core.domain.bookmarks.repositories import BookmarkRepository
from tests.types import Resolver


@pytest.fixture
async def bookmark_repository(resolver: Resolver) -> BookmarkRepository:
    return await resolver(BookmarkRepository)
