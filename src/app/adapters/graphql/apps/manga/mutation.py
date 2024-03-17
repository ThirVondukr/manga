from functools import partial
from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.manga.input import (
    MangaArtsAddInputGQL,
    MangaCreateInputGQL,
    MangaSetCoverArtInputGQL,
    MangaUpdateInputGQL,
)
from app.adapters.graphql.apps.manga.payload import (
    MangaArtsAddPayloadGQL,
    MangaBookmarkPayloadGQL,
    MangaCreatePayloadGQL,
    MangaSetCoverArtPayloadGQL,
    MangaUpdatePayloadGQL,
)
from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import (
    NotFoundErrorGQL,
    map_error_to_gql,
)
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.validation import validate_callable
from app.core.domain.manga.art.command import (
    AddArtsToMangaCommand,
    MangaSetCoverArtCommand,
)
from app.core.domain.manga.bookmarks.commands import (
    MangaBookmarkAddCommand,
    MangaBookmarkRemoveCommand,
)
from app.core.domain.manga.manga.commands import (
    MangaCreateCommand,
    MangaUpdateCommand,
)
from app.settings import AppSettings
from lib.files import FileReader
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
        if isinstance(dto := validate_callable(input.to_dto), Err):
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
    async def update(
        self,
        input: MangaUpdateInputGQL,
        command: Annotated[MangaUpdateCommand, Inject],
        info: Info,
    ) -> MangaUpdatePayloadGQL:
        if isinstance(dto := validate_callable(input.to_dto), Err):
            return MangaUpdatePayloadGQL(error=dto.err_value)

        manga = await command.execute(
            dto=dto.ok_value,
            user=await info.context.user,
        )
        if isinstance(manga, Err):
            return MangaUpdatePayloadGQL(
                error=map_error_to_gql(manga.err_value),
            )

        return MangaUpdatePayloadGQL(
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
        if isinstance(manga_id := validate_uuid(id), Err):
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

    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def add_arts(
        self,
        input: MangaArtsAddInputGQL,
        command: Annotated[AddArtsToMangaCommand, Inject],
        info: Info,
        settings: Annotated[AppSettings, Inject],
    ) -> MangaArtsAddPayloadGQL:
        reader = FileReader(max_size=settings.max_upload_size_bytes)
        files = await reader.read([art.image for art in input.arts])
        if isinstance(files, Err):  # pragma: no cover
            return MangaArtsAddPayloadGQL(
                error=map_error_to_gql(files.err_value),
            )

        dto = validate_callable(partial(input.to_dto, files.ok_value))
        if isinstance(dto, Err):
            return MangaArtsAddPayloadGQL(error=dto.err_value)

        result = await command.execute(
            user=await info.context.user,
            dto=dto.ok_value,
        )
        if isinstance(result, Err):
            return MangaArtsAddPayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return MangaArtsAddPayloadGQL(
            manga=MangaGQL.from_dto(result.ok_value),
        )

    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def set_cover_art(
        self,
        input: MangaSetCoverArtInputGQL,
        info: Info,
        command: Annotated[MangaSetCoverArtCommand, Inject],
    ) -> MangaSetCoverArtPayloadGQL:
        if isinstance(dto := validate_callable(input.to_dto), Err):
            return MangaSetCoverArtPayloadGQL(error=dto.err_value)

        result = await command.execute(
            dto=dto.ok_value,
            user=await info.context.user,
        )
        if isinstance(result, Err):
            return MangaSetCoverArtPayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return MangaSetCoverArtPayloadGQL(
            manga=MangaGQL.from_dto(result.ok_value),
        )
