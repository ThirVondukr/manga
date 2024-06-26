from collections.abc import Sequence
from pathlib import PurePath
from typing import Annotated, Self

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from strawberry import Private

from app.adapters.graphql.dto import DTOMixin
from app.core.storage import FileStorage
from app.db.models import Image, ImageSet


@strawberry.type(name="Image")
class ImageGQL(DTOMixin[Image]):
    _path: Private[PurePath]
    id: strawberry.ID
    width: int
    height: int

    @classmethod
    def from_dto(cls, model: Image) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            _path=model.path,
            width=model.width,
            height=model.height,
        )

    @strawberry.field
    @inject
    async def url(self, storage: Annotated[FileStorage, Inject]) -> str:
        return await storage.url(path=self._path.as_posix())


@strawberry.type(name="ImageSet")
class ImageSetGQL(DTOMixin[ImageSet]):
    id: strawberry.ID
    original: ImageGQL
    alternatives: Sequence[ImageGQL]

    @classmethod
    def from_images(cls, images: Sequence[Image]) -> Self:
        image = max(images, key=lambda image: image.width)
        return cls(
            id=strawberry.ID(str(image.id)),
            original=ImageGQL.from_dto(image),
            alternatives=ImageGQL.from_dto_list(images),
        )

    @classmethod
    def from_dto(cls, model: ImageSet) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            original=ImageGQL.from_dto(model.original),
            alternatives=ImageGQL.from_dto_list(model.images),
        )
