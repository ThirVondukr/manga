import dataclasses

import strawberry

from app.adapters.graphql.types import MangaStatusGQL, SortDirectionGQL
from app.core.domain.manga.dto import MangaCreateDTO
from app.core.domain.manga.filters import (
    MangaFilter,
    MangaSortField,
    Sort,
    TagFilter,
)


@strawberry.input(name="MangaTagFilter")
class MangaTagFilterGQL:
    include: list[str] | None = None
    exclude: list[str] | None = None

    def to_dto(self) -> TagFilter:
        return TagFilter(
            include=self.include,
            exclude=self.exclude,
        )


@strawberry.input(name="MangaFilter")
@dataclasses.dataclass(frozen=True)
class MangaFilterGQL:
    status: MangaStatusGQL | None = None
    search_term: str | None = None
    tags: MangaTagFilterGQL | None = None

    def to_dto(self) -> MangaFilter:
        return MangaFilter(
            status=self.status,
            search_term=self.search_term,
            tags=self.tags.to_dto() if self.tags else TagFilter(),
        )


MangaSortFieldGQL = strawberry.enum(MangaSortField, name="MangaSortField")


@strawberry.input(name="MangaSort")
@dataclasses.dataclass(unsafe_hash=True)
class MangaSortGQL:
    field: MangaSortFieldGQL = MangaSortFieldGQL.title
    direction: SortDirectionGQL = SortDirectionGQL.asc

    def to_dto(self) -> Sort[MangaSortField]:
        return Sort(
            field=self.field,
            direction=self.direction,
        )


@strawberry.federation.input(name="MangaCreateInput")
class MangaCreateInput:
    title: str
    status: MangaStatusGQL

    def to_dto(self) -> MangaCreateDTO:
        return MangaCreateDTO(
            title=self.title,
            status=self.status,
        )
