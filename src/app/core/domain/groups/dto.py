from typing import Annotated

from pydantic import StringConstraints

from app.core.domain.const import GENERIC_NAME_LENGTH
from lib.dto import BaseDTO


class GroupCreateDTO(BaseDTO):
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            max_length=GENERIC_NAME_LENGTH,
        ),
    ]
