from typing import Self

import strawberry

from app.core.errors import (
    EntityAlreadyExistsError,
    PermissionDeniedError,
    RelationshipNotFoundError,
)


@strawberry.interface(name="Error")
class ErrorGQL:
    message: str


@strawberry.type(name="EntityAlreadyExistsError")
class EntityAlreadyExistsErrorGQL(ErrorGQL):
    message: str = "Entity already exists"

    @classmethod
    def from_err(cls, err: EntityAlreadyExistsError) -> Self:  # noqa: ARG003
        return cls()


@strawberry.type(name="RelationshipNotFoundError")
class RelationshipNotFoundErrorGQL(ErrorGQL):
    entity_id: strawberry.ID
    message: str = "Relationship not found"

    @classmethod
    def from_err(cls, err: RelationshipNotFoundError) -> Self:
        return cls(
            entity_id=strawberry.ID(err.entity_id),
        )


@strawberry.type(name="PermissionDeniedError")
class PermissionDeniedErrorGQL(ErrorGQL):
    message: str = "Permission Denied"

    @classmethod
    def from_err(cls, err: PermissionDeniedError) -> Self:  # noqa: ARG003
        return cls()


@strawberry.type(name="NotFoundError")
class NotFoundErrorGQL(ErrorGQL):
    entity_id: strawberry.ID
    message: str = "Entity not found"


@strawberry.type(name="InvalidCredentialsError")
class InvalidCredentialsErrorGQL(ErrorGQL):
    message: str = "Invalid credentials"
