import dataclasses
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.db.models import Manga, MangaRating
from lib.dto import BaseDTO


class MangaSetRatingDTO(BaseDTO):
    manga_id: UUID
    rating: Annotated[int, Field(ge=1, le=10)] | None


@dataclasses.dataclass
class MangaSetRatingResult:
    manga: Manga
    rating: MangaRating | None
