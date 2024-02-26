from typing import Self

import strawberry

from app.adapters.graphql.dto import DTOMixin
from app.db.models import Group


@strawberry.type(name="Group")
class GroupGQL(DTOMixin[Group]):
    id: strawberry.ID
    name: str

    @classmethod
    def from_dto(cls, model: Group) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
        )
