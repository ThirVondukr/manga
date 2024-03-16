from aioinject import Scoped

from app.core.domain.art.command import AddArtsToMangaCommand
from app.core.domain.art.services import MangaArtService
from lib.types import Providers

providers: Providers = [
    Scoped(AddArtsToMangaCommand),
    Scoped(MangaArtService),
]
