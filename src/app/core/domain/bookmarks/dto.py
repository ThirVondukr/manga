import dataclasses

from app.db.models import Manga, MangaBookmark


@dataclasses.dataclass(kw_only=True, slots=True)
class BookmarkMangaResultDTO:
    bookmark: MangaBookmark
    manga: Manga
