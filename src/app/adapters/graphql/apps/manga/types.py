import random
from collections.abc import Sequence
from datetime import datetime
from pathlib import PurePath
from typing import Annotated, Self
from uuid import UUID

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from strawberry import Private

from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.pagination import (
    PagePaginationInputGQL,
    PagePaginationResultGQL,
    map_page_pagination,
)
from app.adapters.graphql.types import LanguageGQL, MangaStatusGQL
from app.core.domain.images.loaders import ImageLoader
from app.core.domain.manga.bookmarks.loaders import (
    MangaBookmarkLoader,
    MangaBookmarkLoaderKey,
)
from app.core.domain.manga.chapters.queries import MangaChaptersQuery
from app.core.domain.manga.manga.loaders import (
    MangaAltTitleLoader,
    MangaArtLoader,
    MangaArtsLoader,
    MangaTagLoader,
)
from app.core.storage import FileStorage
from app.db.models import (
    AltTitle,
    Image,
    Manga,
    MangaArt,
    MangaBookmark,
    MangaRating,
    MangaTag,
)


@strawberry.type(name="MangaTagCategory")
class MangaTagCategoryGQL:
    id: strawberry.ID
    name: str


@strawberry.type(name="MangaTag")
class MangaTagGQL(DTOMixin[MangaTag]):
    id: strawberry.ID
    name: str
    slug: str
    category: MangaTagCategoryGQL

    @classmethod
    def from_dto(cls, model: MangaTag) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            slug=model.name_slug,
            category=MangaTagCategoryGQL(
                id=strawberry.ID(model.category.name),
                name=model.category.name.capitalize(),
            ),
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


@strawberry.type(name="MangaBookmark")
class MangaBookmarkGQL(DTOMixin[MangaBookmark]):
    id: strawberry.ID
    created_at: datetime

    @classmethod
    def from_dto(cls, model: MangaBookmark) -> Self:
        return cls(
            id=strawberry.ID(f"{model.manga_id}:{model.user_id}"),
            created_at=model.created_at,
        )


@strawberry.type(name="Image")
class ImageGQL(DTOMixin[Image]):
    _path: Private[PurePath]
    id: strawberry.ID
    width: int
    height: int

    @classmethod
    def from_dto(cls, model: Image) -> Self:
        w, h = model.dimensions
        return cls(
            id=strawberry.ID(str(model.id)),
            _path=model.path,
            width=w,
            height=h,
        )

    @strawberry.field
    @inject
    async def url(self, storage: Annotated[FileStorage, Inject]) -> str:
        return await storage.url(path=self._path.as_posix())


@strawberry.type(name="MangaArt")
class MangaArtGQL(DTOMixin[MangaArt]):
    _image_id: Private[UUID]
    _preview_image_id: Private[UUID]

    id: strawberry.ID
    volume: int
    language: LanguageGQL

    @classmethod
    def from_dto(cls, model: MangaArt) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            volume=model.volume,
            language=model.language,
            _image_id=model.image_id,
            _preview_image_id=model.preview_image_id,
        )

    @strawberry.field
    async def image(self, info: Info) -> ImageGQL:
        image = await info.context.loaders.map(ImageLoader).load(
            key=self._image_id,
        )
        if not image:  # pragma: no cover
            raise ValueError
        return ImageGQL.from_dto(image)

    @strawberry.field
    async def preview_image(self, info: Info) -> ImageGQL:
        image = await info.context.loaders.map(ImageLoader).load(
            key=self._preview_image_id,
        )
        if not image:  # pragma: no cover
            raise ValueError
        return ImageGQL.from_dto(image)


@strawberry.type(name="MangaRating")
class MangaRatingGQL(DTOMixin[MangaRating]):
    id: strawberry.ID
    value: int

    @classmethod
    def from_dto(cls, model: MangaRating) -> Self:
        return cls(
            id=strawberry.ID(f"{model.manga_id}:{model.user_id}"),
            value=model.rating,
        )


@strawberry.type(name="Manga")
class MangaGQL(DTOMixin[Manga]):
    _instance: Private[Manga]

    id: strawberry.ID
    title: str
    title_slug: str
    description: str
    status: MangaStatusGQL
    created_at: datetime
    updated_at: datetime
    bookmark_count: int
    rating: float
    rating_count: int

    @classmethod
    def from_dto(cls, model: Manga) -> Self:
        return cls(
            _instance=model,
            id=strawberry.ID(str(model.id)),
            title=model.title,
            title_slug=model.title_slug,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            bookmark_count=model.bookmark_count,
            rating=model.rating,
            rating_count=model.rating_count,
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
    @inject
    async def chapters(
        self,
        *,
        pagination: PagePaginationInputGQL | None = None,
        query: Annotated[MangaChaptersQuery, Inject],
    ) -> PagePaginationResultGQL[MangaChapterGQL]:
        pagination = pagination or PagePaginationInputGQL()
        result = await query.execute(
            manga_id=self._instance.id,
            pagination=pagination.to_dto(),
        )
        return map_page_pagination(pagination=result, model_cls=MangaChapterGQL)

    @strawberry.field
    async def alt_titles(self, info: Info) -> Sequence[AltTitleGQL]:
        alt_titles = await info.context.loaders.map(MangaAltTitleLoader).load(
            self._instance.id,
        )
        return AltTitleGQL.from_dto_list(alt_titles)

    @strawberry.field
    async def comment_count(self) -> int:  # pragma: no cover
        random.seed(self.id)
        return random.randint(0, 1000)  # noqa: S311

    @strawberry.field(extensions=[AuthExtension])  # type: ignore[misc]
    async def bookmark(self, info: Info) -> MangaBookmarkGQL | None:
        bookmark = await info.context.loaders.map(MangaBookmarkLoader).load(
            MangaBookmarkLoaderKey(
                manga_id=self._instance.id,
                user_id=info.context.access_token.sub,
            ),
        )
        return MangaBookmarkGQL.from_dto_optional(bookmark)

    @strawberry.field
    async def arts(self, info: Info) -> Sequence[MangaArtGQL]:
        arts = await info.context.loaders.map(MangaArtsLoader).load(
            self._instance.id,
        )
        return MangaArtGQL.from_dto_list(arts)

    @strawberry.field
    async def cover_art(self, info: Info) -> MangaArtGQL | None:
        if self._instance.cover_art_id is None:  # pragma: no cover
            return None

        art = await info.context.loaders.map(MangaArtLoader).load(
            self._instance.cover_art_id,
        )
        return MangaArtGQL.from_dto_optional(art)
