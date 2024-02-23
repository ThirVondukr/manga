from collections.abc import Sequence
from datetime import datetime
from typing import Self

import strawberry
from strawberry import Private

from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.adapters.graphql.types import LanguageGQL
from app.core.domain.manga.loaders import MangaTagLoader
from app.db.models import Manga
from app.db.models._manga import AltTitle, MangaTag


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
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, model: Manga) -> Self:
        return cls(
            _instance=model,
            id=strawberry.ID(str(model.id)),
            title=model.title,
            title_slug=model.title_slug,
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

    # @strawberry.field
    # async def infos(self, info: Info) -> Sequence[AltTitleGQL]:
    #     preferred_languages = preferred_languages or []
    #     preferred_languages = [Language[lang.value] for lang in preferred_languages]
    #     infos = await info.context.loaders.manga_info_by_manga_id.load(self.id)
    #     if preferred_languages:
    #         preferred_infos = [
    #             info for info in infos if info.language in preferred_languages
    #         ]
    #         preferred_infos.sort(
    #             key=lambda i: preferred_languages.index(i.language),
    #         )
    #         infos = preferred_infos or infos
    #
    #     return AltTitleGQL.from_orm_list(infos)

    #
    # @strawberry.field
    # async def chapters(
    #     self,
    #     page: int = 1,
    #     page_size: int = 100,
    # ) -> PagePaginationResult[MangaChapterGQL]:
    #     stmt = MangaChapterService.manga_chapters_query(self._instance.id)
    #     async with async_session_factory() as session:
    #         return await page_paginate(
    #             query=stmt,
    #             page=page,
    #             page_size=page_size,
    #             session=session,
    #             type_=MangaChapterGQL,
    #         )
