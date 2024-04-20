from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from strawberry import Private

from app.adapters.graphql.apps.images.types import ImageSetGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.core.domain.images.loaders import ImageSetLoader
from app.db.models import User


@strawberry.interface(name="User")
class UserGQL:
    _avatar_id: Private[UUID | None]
    id: strawberry.ID
    username: str
    joined_at: datetime

    @strawberry.field
    async def avatar(
        self,
        info: Info,
    ) -> ImageSetGQL | None:  # pragma: no cover
        if self._avatar_id is None:
            return None
        image_set = await info.context.loaders.map(ImageSetLoader).load(
            self._avatar_id,
        )
        return ImageSetGQL.from_dto_optional(image_set)


@strawberry.type(name="PublicUser")
class PublicUserGQL(DTOMixin[User], UserGQL):
    _avatar_id: Private[UUID | None]

    @classmethod
    def from_dto(cls, model: User) -> Self:  # pragma: no cover
        return cls(
            _avatar_id=model.avatar_id,
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
            _avatar_id=model.avatar_id,
            id=strawberry.ID(str(model.id)),
            username=model.username,
            joined_at=model.created_at,
            email=model.email,
        )
