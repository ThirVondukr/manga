from typing import Annotated

import pydantic

from app.core.domain.const import GENERIC_NAME_LENGTH
from lib.dto import BaseDTO


class GroupCreateDTO(BaseDTO):
    name: Annotated[str, pydantic.Field(max_length=GENERIC_NAME_LENGTH)]
