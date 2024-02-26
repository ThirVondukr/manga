from typing import Annotated

import strawberry

from app.adapters.graphql.apps.groups.types import GroupGQL
from app.adapters.graphql.errors import EntityAlreadyExistsErrorGQL
from app.adapters.graphql.validation import ValidationErrorsGQL

GroupCreateError = Annotated[
    ValidationErrorsGQL | EntityAlreadyExistsErrorGQL,
    strawberry.union("GroupCreateError"),
]


@strawberry.type(name="GroupCreatePayload")
class GroupCreatePayloadGQL:
    group: GroupGQL | None = None
    error: GroupCreateError | None
