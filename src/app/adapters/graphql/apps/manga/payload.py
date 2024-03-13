from typing import Annotated

import strawberry

from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.errors import (
    EntityAlreadyExistsErrorGQL,
    NotFoundErrorGQL,
    PermissionDeniedErrorGQL,
)
from app.adapters.graphql.validation import ValidationErrorsGQL

MangaCreateErrorGQL = Annotated[
    ValidationErrorsGQL
    | EntityAlreadyExistsErrorGQL
    | PermissionDeniedErrorGQL,
    strawberry.union("MangaCreateError"),
]


@strawberry.type(name="MangaCreatePayload")
class MangaCreatePayloadGQL:
    manga: MangaGQL | None = None
    error: MangaCreateErrorGQL | None


MangaUpdateErrorGQL = Annotated[
    ValidationErrorsGQL
    | EntityAlreadyExistsErrorGQL
    | PermissionDeniedErrorGQL
    | NotFoundErrorGQL,
    strawberry.union("MangaUpdateError"),
]


@strawberry.type(name="MangaUpdatePayload")
class MangaUpdatePayloadGQL:
    manga: MangaGQL | None = None
    error: MangaUpdateErrorGQL | None


MangaBookmarkErrorGQL = Annotated[
    NotFoundErrorGQL,
    strawberry.union("MangaBookmarkError"),
]


@strawberry.type(name="MangaBookmarkPayload")
class MangaBookmarkPayloadGQL:
    manga: MangaGQL | None = None
    error: MangaBookmarkErrorGQL | None
