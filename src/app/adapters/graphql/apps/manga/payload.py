from typing import Annotated

import strawberry

from app.adapters.graphql.apps.manga.types import MangaGQL, MangaRatingGQL
from app.adapters.graphql.errors import (
    EntityAlreadyExistsErrorGQL,
    FileUploadErrorGQL,
    NotFoundErrorGQL,
    PermissionDeniedErrorGQL,
)
from app.adapters.graphql.validation import (
    ValidationErrorsGQL,
)

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
    NotFoundErrorGQL | ValidationErrorsGQL,
    strawberry.union("MangaBookmarkError"),
]


@strawberry.type(name="MangaBookmarkPayload")
class MangaBookmarkPayloadGQL:
    manga: MangaGQL | None = None
    error: MangaBookmarkErrorGQL | None


MangaArtsAddErrorGQL = Annotated[
    PermissionDeniedErrorGQL
    | NotFoundErrorGQL
    | EntityAlreadyExistsErrorGQL
    | FileUploadErrorGQL
    | ValidationErrorsGQL,
    strawberry.union("MangaArtsAddError"),
]


@strawberry.type(name="MangaArtsAddPayload")
class MangaArtsAddPayloadGQL:
    manga: MangaGQL | None = None
    error: MangaArtsAddErrorGQL | None = None


MangaSetCoverArtErrorGQL = Annotated[
    NotFoundErrorGQL | PermissionDeniedErrorGQL | ValidationErrorsGQL,
    strawberry.union("MangaSetCoverArtErrorGQL"),
]


@strawberry.type(name="MangaSetCoverArtPayload")
class MangaSetCoverArtPayloadGQL:
    manga: MangaGQL | None = None
    error: MangaSetCoverArtErrorGQL | None = None


MangaSetRatingErrorGQL = Annotated[
    NotFoundErrorGQL | ValidationErrorsGQL,
    strawberry.union("MangaSetRatingError"),
]


@strawberry.type(name="MangaSetRatingPayload")
class MangaSetRatingPayloadGQL:
    manga: MangaGQL | None = None
    rating: MangaRatingGQL | None = None
    error: MangaSetRatingErrorGQL | None = None
