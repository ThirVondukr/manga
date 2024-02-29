import random
from collections.abc import Sequence
from datetime import datetime
from typing import Self

import strawberry
from strawberry import Private

from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.adapters.graphql.types import LanguageGQL, MangaStatusGQL
from app.core.domain.manga.loaders import MangaAltTitleLoader, MangaTagLoader
from app.db.models import AltTitle, Manga, MangaTag


@strawberry.federation.type(name="MangaTag")
class MangaTagGQL(DTOMixin[MangaTag]):
    id: strawberry.ID
    name: str
    slug: str

    @classmethod
    def from_dto(cls, model: MangaTag) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            slug=model.name_slug,
        )


@strawberry.type(name="AltTitle")
class AltTitleGQL(DTOMixin[AltTitle]):
    id: strawberry.ID
    language: LanguageGQL
    title: str

    @classmethod
    def from_dto(cls, model: AltTitle) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            language=LanguageGQL(model.language.value),
            title=model.title,
        )


@strawberry.type(name="Manga")
class MangaGQL(DTOMixin[Manga]):
    _instance: Private[Manga]

    id: strawberry.ID
    title: str
    title_slug: str
    status: MangaStatusGQL
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, model: Manga) -> Self:
        return cls(
            _instance=model,
            id=strawberry.ID(str(model.id)),
            title=model.title,
            title_slug=model.title_slug,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    async def tags(
        self,
        info: Info,
    ) -> Sequence[MangaTagGQL]:
        tags = await info.context.loaders.map(MangaTagLoader).load(
            self._instance.id,
        )
        return MangaTagGQL.from_dto_list(tags)

    @strawberry.field
    async def alt_titles(self, info: Info) -> Sequence[AltTitleGQL]:
        alt_titles = await info.context.loaders.map(MangaAltTitleLoader).load(
            self._instance.id,
        )
        return AltTitleGQL.from_dto_list(alt_titles)

    @strawberry.field(description="Manga rating, from 0 to 10")  # type: ignore[misc]
    async def rating(self) -> float:  # pragma: no cover
        random.seed(self.id)
        return random.uniform(0, 10)  # noqa: S311

    @strawberry.field
    async def bookmark_count(self) -> int:  # pragma: no cover
        random.seed(self.id)
        return random.randint(0, 100_000)  # noqa: S311

    @strawberry.field
    async def comment_count(self) -> int:  # pragma: no cover
        random.seed(self.id)
        return random.randint(0, 1000)  # noqa: S311
