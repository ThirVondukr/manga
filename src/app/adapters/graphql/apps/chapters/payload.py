from typing import Annotated

import strawberry

from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.errors import (
    EntityAlreadyExistsErrorGQL,
    FileUploadErrorGQL,
    PermissionDeniedErrorGQL,
    RelationshipNotFoundErrorGQL,
)
from app.adapters.graphql.validation import (
    ValidationErrorsGQL,
)

ChapterCreateError = Annotated[
    ValidationErrorsGQL
    | FileUploadErrorGQL
    | RelationshipNotFoundErrorGQL
    | PermissionDeniedErrorGQL
    | EntityAlreadyExistsErrorGQL,
    strawberry.union(name="ChapterCreateError"),
]


@strawberry.type(name="ChapterCreatePayload")
class ChapterCreatePayloadGQL:
    chapter: MangaChapterGQL | None = None
    error: ChapterCreateError | None
