from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from app.core.domain.const import (
    MANGA_DESCRIPTION_MAX_LENGTH,
    NAME_LENGTH,
)
from lib.dto import BaseDTO
from lib.types import MangaStatus


class MangaCreateDTO(BaseDTO):
    title: Annotated[
        str,
        StringConstraints(
            max_length=NAME_LENGTH,
            strip_whitespace=True,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(
            max_length=MANGA_DESCRIPTION_MAX_LENGTH,
            strip_whitespace=True,
        ),
    ]
    status: MangaStatus


class MangaUpdateDTO(MangaCreateDTO):
    id: UUID
