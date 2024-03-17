from aioinject import Scoped

from app.core.domain.manga.bookmarks.loaders import MangaBookmarkLoader
from app.core.domain.manga.manga.commands import (
    MangaCreateCommand,
    MangaUpdateCommand,
)
from app.core.domain.manga.manga.loaders import (
    MangaAltTitleLoader,
    MangaArtLoader,
    MangaArtsLoader,
    MangaLoader,
    MangaTagLoader,
)
from app.core.domain.manga.manga.queries import MangaSearchQuery
from app.core.domain.manga.manga.repositories import MangaRepository
from app.core.domain.manga.manga.services import MangaPermissions, MangaService
from lib.types import Providers

providers: Providers = [
    # Repositories
    Scoped(MangaRepository),
    # Services
    Scoped(MangaPermissions),
    Scoped(MangaService),
    # Loaders
    Scoped(MangaTagLoader),
    Scoped(MangaArtLoader),
    Scoped(MangaArtsLoader),
    Scoped(MangaAltTitleLoader),
    Scoped(MangaBookmarkLoader),
    Scoped(MangaLoader),
    # Commands/Queries
    Scoped(MangaSearchQuery),
    Scoped(MangaCreateCommand),
    Scoped(MangaUpdateCommand),
]
