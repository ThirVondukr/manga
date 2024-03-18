from aioinject import Scoped

from app.core.domain.manga.ratings.commands import MangaSetRatingCommand
from app.core.domain.manga.ratings.repositories import MangaRatingRepository
from app.core.domain.manga.ratings.services import MangaRatingService
from lib.types import Providers

providers: Providers = [
    Scoped(MangaSetRatingCommand),
    Scoped(MangaRatingService),
    Scoped(MangaRatingRepository),
]
