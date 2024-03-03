from collections.abc import Sequence
from typing import Annotated, Self
from uuid import UUID

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from strawberry import Private

from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.core.domain.chapters.loaders import ChapterPagesLoader
from app.core.storage import ImageStorage
from app.db.models import MangaChapter, MangaPage


@strawberry.type(name="MangaPage")
class MangaPageGQL(DTOMixin[MangaPage]):
    _image_path: Private[str]
    id: strawberry.ID

    number: int

    @classmethod
    def from_dto(cls, model: MangaPage) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            number=model.number,
            _image_path=model.image_path,
        )

    @strawberry.field
    @inject
    async def image(self, storage: Annotated[ImageStorage, Inject]) -> str:
        return await storage.url(path=self._image_path)


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
            number=model.number,
        )

    @strawberry.field
    async def pages(self, info: Info) -> Sequence[MangaPageGQL]:
        pages = await info.context.loaders.map(ChapterPagesLoader).load(
            self._id,
        )
        return MangaPageGQL.from_dto_list(pages)
