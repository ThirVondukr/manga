from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject

from app.adapters.graphql.apps.bookmarks.types import MangaBookmarkGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.pagination import (
    PagePaginationInputGQL,
    PagePaginationResultGQL,
    map_page_pagination,
)
from app.core.domain.manga.bookmarks.queries import UserBookmarksQuery


@strawberry.type
class BookmarkQuery:
    @strawberry.field(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def my_bookmarks(
        self,
        *,
        pagination: PagePaginationInputGQL | None = None,
        info: Info,
        query: Annotated[UserBookmarksQuery, Inject],
    ) -> PagePaginationResultGQL[MangaBookmarkGQL]:
        pagination = pagination or PagePaginationInputGQL()
        result = await query.execute(
            user=info.context.access_token,
            pagination=pagination.to_dto(),
        )
        return map_page_pagination(
            result,
            model_cls=MangaBookmarkGQL,
        )
