from __future__ import annotations

import dataclasses
import random
import uuid
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import factory  # type: ignore[import-untyped]
from faker import Faker

from app.core.domain.types import TagCategory
from app.db.models import Image, User
from app.db.models.manga import (
    AltTitle,
    Manga,
    MangaArt,
    MangaBranch,
    MangaChapter,
    MangaTag,
)
from lib.types import Language, MangaStatus

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
    description = factory.Faker("sentence")
    status = factory.Faker("enum", enum_cls=MangaStatus)
    created_at = factory.Faker("date_time", tzinfo=UTC)


class UserFactory(GenericFactory[User]):
    username = factory.Faker("pystr")
    email = factory.Faker("email")
    password_hash = ""


class ImageFactory(GenericFactory[Image]):
    path = factory.Faker("pystr")
    width = factory.Faker("pyint")
    height = factory.Faker("pyint")


class MangaArtFactory(GenericFactory[MangaArt]):
    volume = factory.Sequence(lambda n: n)
    language = factory.Faker("enum", enum_cls=Language)

    images = factory.LazyFunction(lambda: ImageFactory.create_batch(size=5))


class MangaBranchFactory(GenericFactory[MangaBranch]):
    name = factory.Faker("sentence")
    language = factory.Faker("enum", enum_cls=Language)


class MangaAltTitleFactory(GenericFactory[AltTitle]):
    language = factory.Faker("enum", enum_cls=Language)
    title = factory.Faker("sentence", nb_words=4)


class MangaTagFactory(GenericFactory[MangaTag]):
    name = factory.Faker("text", max_nb_chars=32)
    name_slug = factory.Faker("text", max_nb_chars=32)
    category = factory.Faker("enum", enum_cls=TagCategory)


@dataclasses.dataclass
class _ChapterState:
    volume: int = 1
    number: Sequence[int] = (1, 1)


class ChapterFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake
        self.chapter_numbers: dict[uuid.UUID, _ChapterState] = defaultdict(
            _ChapterState,
        )

    def __call__(
        self,
        branch: MangaBranch,
        created_by: User,
    ) -> MangaChapter:
        state = self.chapter_numbers[branch.id]
        major, minor = state.number
        minor += 1
        if minor > 3:  # noqa: PLR2004
            major += 1
            minor = 0

        state.number = (major, minor)
        if random.random() > 0.9:  # noqa: PLR2004
            state.volume += 1

        return MangaChapter(
            title=self.fake.sentence(),
            created_at=self.fake.date_time(),
            volume=state.volume,
            number=state.number,
            branch=branch,
            created_by=created_by,
            pages=[],
        )
