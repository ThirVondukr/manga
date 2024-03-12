from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.branches.input import MangaBranchCreateInput
from app.adapters.graphql.apps.branches.payload import (
    MangaBranchCreatePayloadGQL,
)
from app.adapters.graphql.apps.branches.types import MangaBranchGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import map_error_to_gql
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.validation import validate_callable
from app.core.domain.branches.commands import MangaBranchCreateCommand


@strawberry.type
class MangaBranchMutationGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(
        self,
        input: MangaBranchCreateInput,
        command: Annotated[MangaBranchCreateCommand, Inject],
        info: Info,
    ) -> MangaBranchCreatePayloadGQL:
        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return MangaBranchCreatePayloadGQL(error=dto.err_value)

        result = await command.execute(
            dto=dto.ok_value,
            user=await info.context.user,
        )

        if isinstance(result, Err):
            return MangaBranchCreatePayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return MangaBranchCreatePayloadGQL(
            branch=MangaBranchGQL.from_dto(result.ok_value),
            error=None,
        )
