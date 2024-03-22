import dataclasses
from uuid import UUID

from app.db.models.manga import Manga, MangaBookmark, MangaBookmarkStatus
from lib.dto import BaseDTO


@dataclasses.dataclass(kw_only=True, slots=True)
class BookmarkMangaResultDTO:
    bookmark: MangaBookmark
    manga: Manga


class BookmarkAddDTO(BaseDTO):
    manga_id: UUID
    status: MangaBookmarkStatus
