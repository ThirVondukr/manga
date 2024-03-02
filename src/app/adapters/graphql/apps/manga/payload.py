from typing import Annotated

import strawberry

from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.errors import NotFoundErrorGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

MangaCreateErrorGQL = Annotated[
    ValidationErrorsGQL,
    strawberry.union("MangaCreateError"),
]


@strawberry.type(name="MangaCreatePayload")
class MangaCreatePayloadGQL:
    manga: MangaGQL | None = None
    error: MangaCreateErrorGQL | None


MangaAddBookmarkErrorGQL = Annotated[
    NotFoundErrorGQL,
    strawberry.union("MangaAddBookmarkError"),
]


@strawberry.type(name="MangaAddBookmarkPayload")
class MangaAddBookmarkPayloadGQL:
    manga: MangaGQL | None = None
    error: MangaAddBookmarkErrorGQL | None
