from datetime import datetime
from typing import Self

import strawberry

from app.adapters.graphql.dto import DTOMixin
from app.db.models import User


@strawberry.interface(name="User")
class UserGQL:
    id: strawberry.ID
    username: str
    joined_at: datetime


@strawberry.type(name="PublicUser")
class PublicUserGQL(DTOMixin[User], UserGQL):

    @classmethod
    def from_dto(cls, model: User) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            username=model.username,
            joined_at=model.created_at,
        )


@strawberry.type(name="PrivateUser")
class PrivateUserGQL(DTOMixin[User], UserGQL):
    email: str

    @classmethod
    def from_dto(cls, model: User) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            username=model.username,
            joined_at=model.created_at,
            email=model.email,
        )
