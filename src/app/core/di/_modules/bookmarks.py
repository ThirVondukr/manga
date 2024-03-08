from aioinject import Scoped

from app.core.domain.bookmarks.commands import (
    MangaBookmarkAddCommand,
    MangaBookmarkRemoveCommand,
)
from app.core.domain.bookmarks.repositories import BookmarkRepository
from app.core.domain.bookmarks.services import BookmarkService
from lib.types import Providers

providers: Providers = [
    Scoped(BookmarkRepository),
    Scoped(BookmarkService),
    Scoped(MangaBookmarkAddCommand),
    Scoped(MangaBookmarkRemoveCommand),
]