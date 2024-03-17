from aioinject import Scoped

from app.core.domain.manga.tags.query import AllMangaTagsQuery
from app.core.domain.manga.tags.repository import MangaTagRepository
from lib.types import Providers

providers: Providers = [
    Scoped(MangaTagRepository),
    Scoped(AllMangaTagsQuery),
]
