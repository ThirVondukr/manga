import dataclasses

import strawberry

from app.adapters.graphql.types import MangaStatusGQL
from app.core.domain.manga.dto import MangaCreateDTO
from app.core.domain.manga.filters import MangaFilter, TagFilter


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


@strawberry.federation.input(name="MangaCreateInput")
class MangaCreateInput:
    title: str
    status: MangaStatusGQL

    def to_dto(self) -> MangaCreateDTO:
        return MangaCreateDTO(
            title=self.title,
            status=self.status,
        )
