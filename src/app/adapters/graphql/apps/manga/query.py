from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.manga.input import MangaFilterGQL, MangaSortGQL
from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.pagination import (
    PagePaginationInputGQL,
    PagePaginationResultGQL,
    map_page_pagination,
)
from app.core.domain.manga.loaders import MangaLoader
from app.core.domain.manga.queries import MangaSearchQuery
from lib.validators import validate_uuid


@strawberry.type
class MangaQuery:
    @strawberry.field
    @inject
    async def manga(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MangaGQL | None:
        validated_id = validate_uuid(id)
        if isinstance(validated_id, Err):
            return None

        manga = await info.context.loaders.map(MangaLoader).load(
            validated_id.ok_value,
        )
        return MangaGQL.from_dto_optional(manga)

    @strawberry.field
    @inject
    async def mangas(
        self,
        *,
        pagination: PagePaginationInputGQL | None = None,
        filter: MangaFilterGQL | None = None,
        sort: MangaSortGQL | None = None,
        query: Annotated[MangaSearchQuery, Inject],
    ) -> PagePaginationResultGQL[MangaGQL]:
        pagination = pagination or PagePaginationInputGQL()
        filter = filter or MangaFilterGQL()
        sort = sort or MangaSortGQL()

        result = await query.execute(
            pagination=pagination.to_dto(),
            filter=filter.to_dto(),
            sort=sort.to_dto(),
        )
        return map_page_pagination(
            pagination=result,
            model_cls=MangaGQL,
        )
