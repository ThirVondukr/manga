import dataclasses

import strawberry

from app.adapters.graphql.apps.manga.input import MangaFilterGQL
from app.adapters.graphql.types import MangaBookmarkStatusGQL, SortDirectionGQL
from app.core.domain.manga.manga.filters import (
    MangaBookmarkFilter,
    MangaBookmarkSortField,
    Sort,
)


@strawberry.input(name="MangaBookmarkFilter")
class MangaBookmarkFilterGQL:
    manga: MangaFilterGQL | None = None
    statuses: list[MangaBookmarkStatusGQL] | None = None

    def to_dto(self) -> MangaBookmarkFilter:
        return MangaBookmarkFilter(
            manga=self.manga.to_dto() if self.manga else None,
            statuses=self.statuses,
        )


MangaBookmarkSortFieldGQL = strawberry.enum(
    MangaBookmarkSortField,
    name="MangaBookmarkSortField",
)


@strawberry.input(name="MangaBookmarkSort")
@dataclasses.dataclass(frozen=True)
class MangaBookmarkSortGQL:
    field: MangaBookmarkSortFieldGQL = MangaBookmarkSortFieldGQL.chapter_upload
    direction: SortDirectionGQL = SortDirectionGQL.desc

    def to_dto(self) -> Sort[MangaBookmarkSortField]:
        return Sort(
            field=self.field,
            direction=self.direction,
        )
