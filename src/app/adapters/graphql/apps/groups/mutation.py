from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.groups.input import GroupCreateInputGQL
from app.adapters.graphql.apps.groups.payload import GroupCreatePayloadGQL
from app.adapters.graphql.apps.groups.types import GroupGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import map_error_to_gql
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.validation import validate_callable
from app.core.domain.groups.commands import GroupCreateCommand


@strawberry.type(name="GroupMutations")
class GroupMutationsGQL:

    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(
        self,
        command: Annotated[GroupCreateCommand, Inject],
        input: GroupCreateInputGQL,
        info: Info,
    ) -> GroupCreatePayloadGQL:
        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return GroupCreatePayloadGQL(error=dto.err_value)

        result = await command.execute(
            dto=dto.ok_value,
            user=await info.context.user,
        )
        if isinstance(result, Err):
            return GroupCreatePayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return GroupCreatePayloadGQL(
            group=GroupGQL.from_dto(result.ok_value),
            error=None,
        )
