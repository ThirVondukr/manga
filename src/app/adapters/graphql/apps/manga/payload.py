from typing import Annotated

import strawberry

from app.adapters.graphql.apps.manga.types import MangaGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

MangaCreateErrorGQL = Annotated[
    ValidationErrorsGQL,
    strawberry.union("MangaCreateError"),
]


@strawberry.federation.type(name="MangaCreatePayload")
class MangaCreatePayloadGQL:
    manga: MangaGQL | None = None
    error: MangaCreateErrorGQL | None
