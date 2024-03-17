from aioinject import Scoped

from app.core.domain.manga.chapters.loaders import (
    ChapterLoader,
    ChapterPagesLoader,
)
from lib.types import Providers

providers: Providers = [
    Scoped(ChapterLoader),
    Scoped(ChapterPagesLoader),
]
