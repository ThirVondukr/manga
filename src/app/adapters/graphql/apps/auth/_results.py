from typing import Annotated

import strawberry

from app.adapters.graphql.apps.users.types import PrivateUserGQL
from app.adapters.graphql.errors import (
    EntityAlreadyExistsErrorGQL,
    InvalidCredentialsErrorGQL,
)
from app.adapters.graphql.validation import ValidationErrorsGQL

SignUpErrorsGQL = Annotated[
    EntityAlreadyExistsErrorGQL | ValidationErrorsGQL,
    strawberry.union(name="SignUpErrors"),
]

SignInErrorsGQL = Annotated[
    InvalidCredentialsErrorGQL | ValidationErrorsGQL,
    strawberry.union(name="SignInErrors"),
]


@strawberry.type(name="AuthenticationResult")
class AuthenticationResultGQL:
    user: PrivateUserGQL
    access_token: str


@strawberry.type(name="SignUpPayload")
class SignUpPayloadGQL:
    result: AuthenticationResultGQL | None = None
    error: SignUpErrorsGQL | None


@strawberry.type(name="SignInPayload")
class SignInPayloadGQL:
    result: AuthenticationResultGQL | None = None
    error: SignInErrorsGQL | None
