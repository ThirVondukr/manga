from aioinject import Scoped

from app.core.domain.chapters.commands import ChapterCreateCommand
from app.core.domain.chapters.queries import MangaChaptersQuery
from app.core.domain.chapters.repositories import MangaChapterRepository
from app.core.domain.chapters.services import ChapterService
from lib.types import Providers

providers: Providers = [
    Scoped(ChapterService),
    Scoped(ChapterCreateCommand),
    Scoped(MangaChapterRepository),
    Scoped(MangaChaptersQuery),
]
