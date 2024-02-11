from typing import Annotated

import strawberry

from app.adapters.graphql.apps.users.types import UserGQL
from app.adapters.graphql.errors import EntityAlreadyExistsErrorGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

RegisterErrorsGQL = Annotated[
    EntityAlreadyExistsErrorGQL | ValidationErrorsGQL,
    strawberry.union(name="UserRegisterErrors"),
]


@strawberry.type(name="UserAndToken")
class UserAndTokenGQL:
    user: UserGQL
    access_token: str


@strawberry.type(name="UserRegisterResult")
class RegisterResultGQL:
    result: UserAndTokenGQL | None = None
    error: RegisterErrorsGQL | None
