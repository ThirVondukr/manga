from collections.abc import Callable
from typing import TypeVar

import pydantic
import strawberry
from pydantic import BaseModel
from result import Err, Ok, Result

from app.adapters.graphql.errors import ErrorGQL

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)
T = TypeVar("T")


@strawberry.type(name="ValidationError")
class ValidationError(ErrorGQL):
    code: str
    message: str
    location: list[str]


@strawberry.type(name="ValidationErrors")
class ValidationErrorsGQL(ErrorGQL):
    message: str = "Validation Error"
    errors: list[ValidationError] = strawberry.field(default_factory=list)


@strawberry.type(name="FileUploadError")
class FileUploadErrorGQL(ErrorGQL):
    message: str = "Invalid file"


def _to_graphql_error(
    exception: pydantic.ValidationError,
) -> ValidationErrorsGQL:
    errors = [
        ValidationError(
            location=list(map(str, error["loc"])),
            message=error["msg"],
            code=error["type"],
        )
        for error in exception.errors()
    ]
    return ValidationErrorsGQL(errors=errors)


def validate_callable(
    callable_: Callable[[], T],
) -> Result[T, ValidationErrorsGQL]:
    try:
        return Ok(callable_())
    except pydantic.ValidationError as exc:
        return Err(_to_graphql_error(exc))
