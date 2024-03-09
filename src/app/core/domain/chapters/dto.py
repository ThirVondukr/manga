from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from pydantic import ConfigDict, Field, StringConstraints

from app.core.domain.const import GENERIC_NAME_LENGTH, GENERIC_NAME_MIN_LENGTH
from lib.dto import BaseDTO
from lib.files import File


class ChapterCreateDTO(BaseDTO):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    branch_id: UUID

    title: Annotated[
        str,
        StringConstraints(
            min_length=GENERIC_NAME_MIN_LENGTH,
            max_length=GENERIC_NAME_LENGTH,
            strip_whitespace=True,
        ),
    ]
    volume: Annotated[int | None, Field(gt=0)]
    number: Annotated[
        Sequence[Annotated[int, Field(gt=0)]],
        Field(min_length=1, max_length=2),
    ]
    pages: Annotated[Sequence[File], Field(min_length=1)]
