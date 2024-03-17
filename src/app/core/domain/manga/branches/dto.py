from uuid import UUID

from pydantic import Field

from app.core.domain.const import NAME_LENGTH
from lib.dto import BaseDTO
from lib.types import Language


class MangaBranchCreateDTO(BaseDTO):
    name: str = Field(max_length=NAME_LENGTH)
    manga_id: UUID
    group_id: UUID
    language: Language
