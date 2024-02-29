from collections.abc import Sequence
from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject

from app.adapters.graphql.apps.manga.types import MangaTagGQL
from app.core.domain.tags.query import AllMangaTagsQuery


@strawberry.type
class TagsQueryGQL:
    @strawberry.field
    @inject
    async def tags(
        self,
        query: Annotated[AllMangaTagsQuery, Inject],
    ) -> Sequence[MangaTagGQL]:
        tags = await query.execute()
        return MangaTagGQL.from_dto_list(tags)
