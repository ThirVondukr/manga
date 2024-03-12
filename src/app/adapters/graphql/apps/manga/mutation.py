from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.manga.input import (
    MangaCreateInputGQL,
    MangaUpdateInputGQL,
)
from app.adapters.graphql.apps.manga.payload import (
    MangaBookmarkPayloadGQL,
    MangaCreatePayloadGQL,
)
from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import (
    NotFoundErrorGQL,
    map_error_to_gql,
)
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.validation import validate_callable
from app.core.domain.bookmarks.commands import (
    MangaBookmarkAddCommand,
    MangaBookmarkRemoveCommand,
)
from app.core.domain.manga.commands import MangaCreateCommand
from lib.validators import validate_uuid


@strawberry.type(name="MangaMutations")
class MangaMutationsGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(
        self,
        input: MangaCreateInputGQL,
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
        if isinstance(manga, Err):
            return MangaCreatePayloadGQL(
                error=map_error_to_gql(manga.err_value),
            )

        return MangaCreatePayloadGQL(
            manga=MangaGQL.from_dto(manga.ok_value),
            error=None,
        )

    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def add_bookmark(
        self,
        id: strawberry.ID,
        info: Info,
        command: Annotated[MangaBookmarkAddCommand, Inject],
    ) -> MangaBookmarkPayloadGQL:
        manga_id = validate_uuid(id)
        if isinstance(manga_id, Err):
            return MangaBookmarkPayloadGQL(
                error=NotFoundErrorGQL(entity_id=id),
            )

        result = await command.execute(
            user=await info.context.user,
            manga_id=manga_id.ok_value,
        )
        if isinstance(result, Err):
            return MangaBookmarkPayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return MangaBookmarkPayloadGQL(
            manga=MangaGQL.from_dto(result.ok_value.manga),
            error=None,
        )

    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def remove_bookmark(
        self,
        id: strawberry.ID,
        info: Info,
        command: Annotated[MangaBookmarkRemoveCommand, Inject],
    ) -> MangaBookmarkPayloadGQL:
        manga_id = validate_uuid(id)
        if isinstance(manga_id, Err):
            return MangaBookmarkPayloadGQL(
                error=NotFoundErrorGQL(entity_id=id),
            )
        result = await command.execute(
            user=await info.context.user,
            manga_id=manga_id.ok_value,
        )
        if isinstance(result, Err):
            return MangaBookmarkPayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return MangaBookmarkPayloadGQL(
            manga=MangaGQL.from_dto(result.ok_value),
            error=None,
        )

    @strawberry.mutation
    async def update(self, input: MangaUpdateInputGQL) -> None:
        pass
