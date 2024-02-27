from typing import Annotated

import strawberry

from app.adapters.graphql.apps.branches.types import MangaBranchGQL
from app.adapters.graphql.errors import RelationshipNotFoundErrorGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

MangaBranchCreateError = Annotated[
    ValidationErrorsGQL | RelationshipNotFoundErrorGQL,
    strawberry.union(name="MangaBranchCreateError"),
]


@strawberry.type(name="MangaBranchCreatePayload")
class MangaBranchCreatePayloadGQL:
    branch: MangaBranchGQL | None = None
    error: MangaBranchCreateError | None
