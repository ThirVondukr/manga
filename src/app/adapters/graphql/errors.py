from typing import Self

import strawberry

from app.core.errors import RelationshipNotFoundError


@strawberry.interface(name="Error")
class ErrorGQL:
    message: str


@strawberry.type(name="EntityAlreadyExistsError")
class EntityAlreadyExistsErrorGQL(ErrorGQL):
    message: str = "Entity already exists"


@strawberry.type(name="RelationshipNotFoundError")
class RelationshipNotFoundErrorGQL(ErrorGQL):
    entity_id: strawberry.ID
    message: str = "Relationship not found"

    @classmethod
    def from_err(cls, err: RelationshipNotFoundError) -> Self:
        return cls(
            entity_id=strawberry.ID(err.entity_id),
        )


@strawberry.type(name="NotFoundError")
class NotFoundErrorGQL(ErrorGQL):
    entity_id: strawberry.ID
    message: str = "Entity not found"


@strawberry.type(name="InvalidCredentialsError")
class InvalidCredentialsErrorGQL(ErrorGQL):
    message: str = "Invalid credentials"
