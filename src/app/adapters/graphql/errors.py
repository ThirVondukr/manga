import typing
from typing import Self, assert_never

import strawberry

from app.core.errors import (
    EntityAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
    RelationshipNotFoundError,
)
from lib.files import FileReadError


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


@strawberry.type(name="FileUploadError")
class FileUploadErrorGQL(ErrorGQL):
    message: str

    @classmethod
    def from_error(cls, err: FileReadError) -> Self:
        return cls(message=err.message)


@typing.overload
def map_error_to_gql(error: NotFoundError) -> NotFoundErrorGQL: ...


@typing.overload
def map_error_to_gql(
    error: PermissionDeniedError,
) -> PermissionDeniedErrorGQL: ...


@typing.overload
def map_error_to_gql(
    error: EntityAlreadyExistsError,
) -> EntityAlreadyExistsErrorGQL: ...


@typing.overload
def map_error_to_gql(
    error: RelationshipNotFoundError,
) -> RelationshipNotFoundErrorGQL: ...


@typing.overload
def map_error_to_gql(
    error: FileReadError,
) -> FileUploadErrorGQL: ...


def map_error_to_gql(
    error: (
        NotFoundError
        | PermissionDeniedError
        | EntityAlreadyExistsError
        | RelationshipNotFoundError
        | FileReadError
    ),
) -> (
    NotFoundErrorGQL
    | PermissionDeniedErrorGQL
    | EntityAlreadyExistsErrorGQL
    | RelationshipNotFoundErrorGQL
    | FileUploadErrorGQL
):
    match error:
        case NotFoundError():
            return NotFoundErrorGQL(entity_id=strawberry.ID(error.entity_id))
        case PermissionDeniedError():
            return PermissionDeniedErrorGQL.from_err(error)
        case EntityAlreadyExistsError():
            return EntityAlreadyExistsErrorGQL.from_err(error)
        case RelationshipNotFoundError():
            return RelationshipNotFoundErrorGQL.from_err(error)
        case FileReadError():
            return FileUploadErrorGQL.from_error(error)
        case _:  # pragma: no cover
            assert_never(error)
