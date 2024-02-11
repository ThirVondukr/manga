from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql import auth
from app.adapters.graphql.apps.auth._inputs import RegisterInputGQL
from app.adapters.graphql.apps.auth._results import (
    RegisterResultGQL,
    UserAndTokenGQL,
)
from app.adapters.graphql.apps.users.types import UserGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import EntityAlreadyExistsErrorGQL
from app.adapters.graphql.validation import validate_callable
from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.errors import UserAlreadyExistsError
from app.settings import AuthSettings


@strawberry.type(name="AuthMutations")
class AuthMutationsGQL:
    @strawberry.mutation
    @inject
    async def register(
        self,
        input: RegisterInputGQL,
        command: Annotated[UserRegisterCommand, Inject],
        info: Info,
        auth_settings: Annotated[AuthSettings, Inject],
    ) -> RegisterResultGQL:
        if not info.context.response:
            raise ValueError  # pragma: no cover

        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return RegisterResultGQL(error=dto.err_value)

        result = await command.execute(dto=dto.ok_value)
        if isinstance(result, Err):
            match result.err_value:
                case UserAlreadyExistsError():  # pragma: no branch
                    return RegisterResultGQL(
                        error=EntityAlreadyExistsErrorGQL(),
                    )

        auth.set_cookie(
            response=info.context.response,
            token=result.ok_value.refresh_token,
            cookie_name=auth_settings.refresh_token_cookie,
        )
        return RegisterResultGQL(
            result=UserAndTokenGQL(
                user=UserGQL.from_dto(result.ok_value.user),
                access_token=result.ok_value.access_token.token,
            ),
            error=None,
        )
