import dataclasses
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from lib.types import DatetimeInt


class TokenClaims(BaseModel):
    token_type: Literal["access", "refresh"]
    sub: UUID
    iat: DatetimeInt
    exp: DatetimeInt


@dataclasses.dataclass
class TokenWrapper:
    claims: TokenClaims
    token: str
