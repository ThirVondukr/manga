from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject

from app.adapters.graphql.apps.bookmarks.input import (
    MangaBookmarkFilterGQL,
    MangaBookmarkSortGQL,
)
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
    async def my_bookmarks(  # noqa: PLR0913
        self,
        *,
        pagination: PagePaginationInputGQL | None = None,
        filter: MangaBookmarkFilterGQL | None = None,
        sort: MangaBookmarkSortGQL | None = None,
        info: Info,
        query: Annotated[UserBookmarksQuery, Inject],
    ) -> PagePaginationResultGQL[MangaBookmarkGQL]:
        filter = filter or MangaBookmarkFilterGQL()
        pagination = pagination or PagePaginationInputGQL()
        sort = sort or MangaBookmarkSortGQL()

        result = await query.execute(
            filter=filter.to_dto(),
            user=info.context.access_token,
            pagination=pagination.to_dto(),
            sort=sort.to_dto(),
        )
        return map_page_pagination(
            result,
            model_cls=MangaBookmarkGQL,
        )
