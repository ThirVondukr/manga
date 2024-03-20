from collections.abc import Sequence
from typing import Self
from uuid import UUID

import strawberry
from strawberry import Private

from app.adapters.graphql.apps.images.types import ImageSetGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.core.domain.manga.chapters.loaders import (
    ChapterPagesLoader,
    MangaPageImagesLoader,
)
from app.db.models.manga import MangaChapter, MangaPage


@strawberry.type(name="MangaPage")
class MangaPageGQL(DTOMixin[MangaPage]):
    _id: UUID
    id: strawberry.ID

    number: int

    @classmethod
    def from_dto(cls, model: MangaPage) -> Self:
        return cls(
            _id=model.id,
            id=strawberry.ID(str(model.id)),
            number=model.number,
        )

    @strawberry.field
    async def image(self, info: Info) -> ImageSetGQL:
        images = await info.context.loaders.map(MangaPageImagesLoader).load(
            self._id,
        )
        return ImageSetGQL.from_images(images)


@strawberry.type(name="MangaChapter")
class MangaChapterGQL(DTOMixin[MangaChapter]):
    _id: Private[UUID]
    id: strawberry.ID

    title: str
    volume: int | None
    number: str

    @classmethod
    def from_dto(cls, model: MangaChapter) -> Self:
        return cls(
            _id=model.id,
            id=strawberry.ID(str(model.id)),
            title=model.title,
            volume=model.volume,
            number=".".join(str(n) for n in model.number),
        )

    @strawberry.field
    async def pages(self, info: Info) -> Sequence[MangaPageGQL]:
        pages = await info.context.loaders.map(ChapterPagesLoader).load(
            self._id,
        )
        return MangaPageGQL.from_dto_list(pages)
