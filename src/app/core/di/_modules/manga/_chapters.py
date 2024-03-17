from aioinject import Scoped

from app.core.domain.manga.chapters.commands import ChapterCreateCommand
from app.core.domain.manga.chapters.queries import MangaChaptersQuery
from app.core.domain.manga.chapters.repositories import ChapterRepository
from app.core.domain.manga.chapters.services import (
    ChapterPermissionService,
    ChapterService,
)
from lib.types import Providers

providers: Providers = [
    Scoped(ChapterRepository),
    Scoped(ChapterPermissionService),
    Scoped(ChapterService),
    Scoped(ChapterCreateCommand),
    Scoped(MangaChaptersQuery),
]
