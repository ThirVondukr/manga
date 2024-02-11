from pydantic import EmailStr, SecretStr

from app.core.domain.auth.dto import TokenWrapper
from app.db.models import User
from lib.dto import BaseDTO


class UserRegisterDTO(BaseDTO):
    username: str
    password: SecretStr
    email: EmailStr


class UserRegisterResultDTO(BaseDTO):
    user: User
    access_token: TokenWrapper
    refresh_token: TokenWrapper
