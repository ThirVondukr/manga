from pydantic import EmailStr, SecretStr

from lib.dto import BaseDTO


class UserRegisterDTO(BaseDTO):
    username: str
    password: SecretStr
    email: EmailStr
