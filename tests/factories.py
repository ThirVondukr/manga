from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import factory  # type: ignore[import-untyped]
from faker import Faker

from app.db.models import Manga, MangaBranch, MangaChapter, MangaTag

T = TypeVar("T")


class GenericFactory(factory.Factory, Generic[T]):  # type: ignore[misc]
    if TYPE_CHECKING:

        @classmethod
        def build(cls, **kwargs: Any) -> T:  # noqa: ANN401
            ...

        @classmethod
        def build_batch(
            cls,
            size: int,
            **kwargs: Any,  # noqa: ANN401
        ) -> list[T]: ...

    def __class_getitem__(cls, item: T) -> type[GenericFactory[T]]:
        class Meta:
            model = item

        return type(f"{item.__class__.__name__}Factory", (cls,), {"Meta": Meta})


class MangaFactory(GenericFactory[Manga]):
    title = factory.Faker("sentence")
    title_slug = factory.Faker("sentence")
    created_at = factory.Faker("date_time", tzinfo=UTC)


class MangaTagFactory(GenericFactory[MangaTag]):
    name = factory.Faker("word")
    name_slug = factory.Faker("word")


class ChapterFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake
        self.chapter_numbers: dict[uuid.UUID, tuple[int, int]] = defaultdict(
            lambda: (1, 0),
        )

    def __call__(
        self,
        branch: MangaBranch,
        **kwargs: Any,  # noqa: ANN401
    ) -> MangaChapter:
        if not (number := kwargs.pop("number", None)):
            major, minor = self.chapter_numbers[branch.id]
            number = f"{major}.{minor}" if minor else str(major)
            minor += 1
            if minor > 3:  # noqa: PLR2004
                major += 1
                minor = 0
            self.chapter_numbers[branch.id] = (major, minor)

        return MangaChapter(
            title=self.fake.sentence(),
            created_at=self.fake.date_time(),
            number=number,
            branch=branch,
            **kwargs,
        )
