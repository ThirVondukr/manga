import dataclasses
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.db.models import User
from lib.types import DatetimeInt


class TokenClaims(BaseModel):
    sub: UUID
    iat: DatetimeInt
    exp: DatetimeInt
    aud: str
    typ: Literal["Bearer"]
    email: str
    preferred_username: str


@dataclasses.dataclass
class TokenWrapper:
    claims: TokenClaims
    token: str


@dataclasses.dataclass
class AuthResultDTO:
    user: User
    claims: TokenClaims
