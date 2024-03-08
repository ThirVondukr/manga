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
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.types import GraphQLFile
from app.adapters.graphql.validation import validate_callable
from app.core.domain.chapters.commands import ChapterCreateCommand
from lib.files import FileReader


@strawberry.type
class ChapterMutationGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def create(
        self,
        info: Info,
        pages: Sequence[GraphQLFile],
        input: ChapterCreateInputGQL,
        command: Annotated[ChapterCreateCommand, Inject],
    ) -> ChapterCreatePayloadGQL:
        reader = FileReader(max_size=200 * 1024 * 1024)
        pages_result = await reader.read(files=pages)
        if isinstance(pages_result, Err):
            raise ValueError  # noqa: TRY004

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
            raise ValueError  # noqa: TRY004

        return ChapterCreatePayloadGQL(
            chapter=MangaChapterGQL.from_dto(result.ok_value),
            error=None,
        )
