from aioinject import Scoped

from app.core.domain.manga.commands import MangaCreateCommand
from app.core.domain.manga.loaders import (
    MangaAltTitleLoader,
    MangaLoader,
    MangaTagLoader,
)
from app.core.domain.manga.queries import MangaSearchQuery
from app.core.domain.manga.repositories import MangaRepository
from app.core.domain.manga.services import MangaService
from lib.types import Providers

providers: Providers = [
    Scoped(MangaRepository),
    Scoped(MangaService),
    Scoped(MangaSearchQuery),
    Scoped(MangaLoader),
    Scoped(MangaCreateCommand),
    Scoped(MangaTagLoader),
    Scoped(MangaAltTitleLoader),
]
