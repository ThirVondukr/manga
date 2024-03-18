import itertools

from lib.types import Providers

from . import (
    _art,
    _bookmarks,
    _branches,
    _chapters,
    _import,
    _manga,
    _manga_chapters,
    _ratings,
    _tags,
)

providers: Providers = list(
    itertools.chain(
        _art.providers,
        _bookmarks.providers,
        _branches.providers,
        _chapters.providers,
        _import.providers,
        _manga.providers,
        _manga_chapters.providers,
        _ratings.providers,
        _tags.providers,
    ),
)
