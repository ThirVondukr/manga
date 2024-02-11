import dataclasses
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr

from app.db.models import User
from lib.dto import BaseDTO
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


class SignInDTO(BaseDTO):
    email: str
    password: SecretStr


class UserRegisterDTO(BaseDTO):
    username: str
    password: SecretStr
    email: EmailStr


class UserAuthResultDTO(BaseDTO):
    user: User
    access_token: TokenWrapper
    refresh_token: TokenWrapper
