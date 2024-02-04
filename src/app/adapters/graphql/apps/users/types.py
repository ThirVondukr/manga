from typing import Self

import strawberry

from app.adapters.graphql.dto import DTOMixin
from app.db.models import User


@strawberry.type
class UserGQL(DTOMixin[User]):
    id: strawberry.ID
    username: str

    @classmethod
    def from_dto(cls, model: User) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            username=model.username,
        )
