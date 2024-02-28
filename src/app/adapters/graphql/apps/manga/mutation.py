from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.manga.input import MangaCreateInput
from app.adapters.graphql.apps.manga.payload import MangaCreatePayloadGQL
from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.validation import validate_callable
from app.core.domain.manga.commands import MangaCreateCommand


@strawberry.type(name="MangaMutations")
class MangaMutationsGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(
        self,
        input: MangaCreateInput,
        command: Annotated[MangaCreateCommand, Inject],
        info: Info,
    ) -> MangaCreatePayloadGQL:
        dto = validate_callable(input.to_dto)
        if isinstance(dto, Err):
            return MangaCreatePayloadGQL(error=dto.err_value)

        manga = await command.execute(
            dto=dto.ok_value,
            user=await info.context.user,
        )
        return MangaCreatePayloadGQL(manga=MangaGQL.from_dto(manga), error=None)
