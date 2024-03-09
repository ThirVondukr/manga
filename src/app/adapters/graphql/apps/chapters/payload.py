from typing import Annotated

import strawberry

from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.errors import (
    PermissionDeniedErrorGQL,
    RelationshipNotFoundErrorGQL,
)
from app.adapters.graphql.validation import (
    FileUploadErrorGQL,
    ValidationErrorsGQL,
)

ChapterCreateError = Annotated[
    ValidationErrorsGQL
    | FileUploadErrorGQL
    | RelationshipNotFoundErrorGQL
    | PermissionDeniedErrorGQL,
    strawberry.union(name="ChapterCreateError"),
]


@strawberry.type(name="ChapterCreatePayload")
class ChapterCreatePayloadGQL:
    chapter: MangaChapterGQL | None = None
    error: ChapterCreateError | None
