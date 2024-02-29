from aioinject import Scoped

from app.core.domain.tags.query import AllMangaTagsQuery
from app.core.domain.tags.repository import MangaTagRepository
from lib.types import Providers

providers: Providers = [
    Scoped(MangaTagRepository),
    Scoped(AllMangaTagsQuery),
]
