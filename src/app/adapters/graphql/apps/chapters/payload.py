from typing import Annotated

import strawberry

from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

ChapterCreateError = Annotated[
    ValidationErrorsGQL,
    strawberry.union(name="ChapterCreateError"),
]


@strawberry.type(name="ChapterCreatePayload")
class ChapterCreatePayloadGQL:
    chapter: MangaChapterGQL | None
    error: ChapterCreateError | None
