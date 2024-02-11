import strawberry


@strawberry.interface(name="Error")
class ErrorGQL:
    message: str


@strawberry.type(name="EntityAlreadyExistsError")
class EntityAlreadyExistsErrorGQL(ErrorGQL):
    message: str = "Entity already exists"


@strawberry.type(name="InvalidCredentialsError")
class InvalidCredentialsErrorGQL(ErrorGQL):
    message: str = "Invalid credentials"
