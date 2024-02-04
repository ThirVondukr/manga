import strawberry
from pydantic import SecretStr

from app.core.domain.users.dto import UserRegisterDTO


@strawberry.input(name="UserRegisterInput")
class UserRegisterInputGQL:
    email: str
    username: str
    password: str

    def to_dto(self) -> UserRegisterDTO:
        return UserRegisterDTO(
            email=self.email,
            username=self.username,
            password=SecretStr(self.password),
        )
