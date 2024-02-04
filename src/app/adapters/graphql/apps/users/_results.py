from typing import Annotated

import strawberry

from app.adapters.graphql.apps.users.types import UserGQL
from app.adapters.graphql.errors import EntityAlreadyExistsErrorGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

UserRegistrationErrorsGQL = Annotated[
    EntityAlreadyExistsErrorGQL | ValidationErrorsGQL,
    strawberry.union(name="UserRegisterErrors"),
]


@strawberry.type(name="UserRegisterResult")
class UserRegisterResultGQL:
    user: UserGQL | None = None
    error: UserRegistrationErrorsGQL | None
