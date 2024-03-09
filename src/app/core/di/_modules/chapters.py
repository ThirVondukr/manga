from aioinject import Scoped

from app.core.domain.chapters.commands import ChapterCreateCommand
from app.core.domain.chapters.queries import MangaChaptersQuery
from app.core.domain.chapters.repositories import ChapterRepository
from app.core.domain.chapters.services import (
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
