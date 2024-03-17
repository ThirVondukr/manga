from aioinject import Scoped

from app.core.domain.manga.art.command import (
    AddArtsToMangaCommand,
    MangaSetCoverArtCommand,
)
from app.core.domain.manga.art.services import MangaArtService
from lib.types import Providers

providers: Providers = [
    Scoped(AddArtsToMangaCommand),
    Scoped(MangaArtService),
    Scoped(MangaSetCoverArtCommand),
]
