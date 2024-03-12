from collections.abc import Sequence
from functools import partial
from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.chapters.input import ChapterCreateInputGQL
from app.adapters.graphql.apps.chapters.payload import ChapterCreatePayloadGQL
from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import (
    map_error_to_gql,
)
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.types import GraphQLFile
from app.adapters.graphql.validation import (
    FileUploadErrorGQL,
    validate_callable,
)
from app.core.domain.chapters.commands import ChapterCreateCommand
from app.settings import AppSettings
from lib.files import FileReader


@strawberry.type
class ChapterMutationGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(  # noqa: PLR0913
        self,
        info: Info,
        pages: Sequence[GraphQLFile],
        input: ChapterCreateInputGQL,
        command: Annotated[ChapterCreateCommand, Inject],
        settings: Annotated[AppSettings, Inject],
    ) -> ChapterCreatePayloadGQL:
        reader = FileReader(max_size=settings.max_upload_size_bytes)
        pages_result = await reader.read(files=pages)
        if isinstance(pages_result, Err):
            return ChapterCreatePayloadGQL(
                error=FileUploadErrorGQL(),
            )

        dto = validate_callable(
            partial(input.to_dto, pages=pages_result.ok_value),
        )
        if isinstance(dto, Err):
            return ChapterCreatePayloadGQL(
                chapter=None,
                error=dto.err_value,
            )

        result = await command.execute(
            user=await info.context.user,
            dto=dto.ok_value,
        )

        if isinstance(result, Err):
            return ChapterCreatePayloadGQL(
                error=map_error_to_gql(result.err_value),
            )

        return ChapterCreatePayloadGQL(
            chapter=MangaChapterGQL.from_dto(result.ok_value),
            error=None,
        )
