from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.users._inputs import UserRegisterInputGQL
from app.adapters.graphql.apps.users._results import UserRegisterResultGQL
from app.adapters.graphql.apps.users.types import UserGQL
from app.adapters.graphql.errors import EntityAlreadyExistsErrorGQL
from app.adapters.graphql.validation import validate_callable
from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.errors import UserAlreadyExistsError


@strawberry.type(name="UserMutations")
class UserMutationsGQL:
    @strawberry.mutation
    @inject
    async def register(
        self,
        input: UserRegisterInputGQL,
        command: Annotated[UserRegisterCommand, Inject],
    ) -> UserRegisterResultGQL:
        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return UserRegisterResultGQL(error=dto.err_value)

        result = await command.execute(dto=dto.ok_value)
        if isinstance(result, Err):
            match result.err_value:
                case UserAlreadyExistsError():  # pragma: no branch
                    return UserRegisterResultGQL(
                        error=EntityAlreadyExistsErrorGQL(),
                    )
        return UserRegisterResultGQL(
            user=UserGQL.from_dto(result.ok_value),
            error=None,
        )
