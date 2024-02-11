import strawberry
from pydantic import SecretStr

from app.core.domain.auth.dto import SignInDTO, UserRegisterDTO


@strawberry.input(name="SignUpInput")
class SignUpInputGQL:
    email: str
    username: str
    password: str

    def to_dto(self) -> UserRegisterDTO:
        return UserRegisterDTO(
            email=self.email,
            username=self.username,
            password=SecretStr(self.password),
        )


@strawberry.input(name="SignInInput")
class SignInInputGQL:
    email: str
    password: str

    def to_dto(self) -> SignInDTO:
        return SignInDTO(
            email=self.email,
            password=SecretStr(self.password),
        )
