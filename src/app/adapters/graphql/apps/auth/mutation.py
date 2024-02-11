from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql import auth
from app.adapters.graphql.apps.auth._inputs import (
    SignInInputGQL,
    SignUpInputGQL,
)
from app.adapters.graphql.apps.auth._results import (
    AuthenticationResultGQL,
    SignInPayloadGQL,
    SignUpPayloadGQL,
)
from app.adapters.graphql.apps.users.types import UserGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import (
    EntityAlreadyExistsErrorGQL,
    InvalidCredentialsErrorGQL,
)
from app.adapters.graphql.validation import validate_callable
from app.core.domain.auth.commands import SignInCommand
from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.errors import UserAlreadyExistsError
from app.settings import AuthSettings


@strawberry.type(name="AuthMutations")
class AuthMutationsGQL:
    @strawberry.mutation
    @inject
    async def sign_up(
        self,
        input: SignUpInputGQL,
        info: Info,
        command: Annotated[UserRegisterCommand, Inject],
        auth_settings: Annotated[AuthSettings, Inject],
    ) -> SignUpPayloadGQL:
        if not info.context.response:
            raise ValueError  # pragma: no cover

        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return SignUpPayloadGQL(error=dto.err_value)

        result = await command.execute(dto=dto.ok_value)
        if isinstance(result, Err):
            match result.err_value:
                case UserAlreadyExistsError():  # pragma: no branch
                    return SignUpPayloadGQL(
                        error=EntityAlreadyExistsErrorGQL(),
                    )

        auth.set_cookie(
            response=info.context.response,
            token=result.ok_value.refresh_token,
            cookie_name=auth_settings.refresh_token_cookie,
        )
        return SignUpPayloadGQL(
            result=AuthenticationResultGQL(
                user=UserGQL.from_dto(result.ok_value.user),
                access_token=result.ok_value.access_token.token,
            ),
            error=None,
        )

    @strawberry.mutation
    @inject
    async def sign_in(
        self,
        input: SignInInputGQL,
        info: Info,
        command: Annotated[SignInCommand, Inject],
        auth_settings: Annotated[AuthSettings, Inject],
    ) -> SignInPayloadGQL:
        if not info.context.response:
            raise ValueError  # pragma: no cover

        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return SignInPayloadGQL(error=dto.err_value)  # pragma: no cover

        result = await command.execute(dto=dto.ok_value)
        if result is None:
            return SignInPayloadGQL(
                error=InvalidCredentialsErrorGQL(),
            )

        auth.set_cookie(
            response=info.context.response,
            token=result.refresh_token,
            cookie_name=auth_settings.refresh_token_cookie,
        )

        return SignInPayloadGQL(
            result=AuthenticationResultGQL(
                user=UserGQL.from_dto(result.user),
                access_token=result.access_token.token,
            ),
            error=None,
        )
