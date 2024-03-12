from typing import Annotated
from uuid import UUID

from pydantic import Field

from lib.dto import BaseDTO
from lib.types import MangaStatus
from lib.validators import StripWhitespace


class MangaCreateDTO(BaseDTO):
    title: Annotated[str, Field(max_length=250), StripWhitespace]
    status: MangaStatus


class MangaUpdateDTO(MangaCreateDTO):
    id: UUID
