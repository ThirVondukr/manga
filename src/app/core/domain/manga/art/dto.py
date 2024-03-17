from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from pydantic import Field

from lib.dto import BaseDTO
from lib.files import File
from lib.types import Language


class MangaArtAddDTO(BaseDTO):
    image: File
    volume: Annotated[int, Field(ge=0)]
    language: Language


class MangaArtsAddDTO(BaseDTO):
    manga_id: UUID
    arts: Sequence[MangaArtAddDTO]


class MangaSetCoverArtDTO(BaseDTO):
    manga_id: UUID
    art_id: UUID | None
