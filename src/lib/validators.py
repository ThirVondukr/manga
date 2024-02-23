from uuid import UUID

from pydantic import BeforeValidator
from result import Err, Ok, Result


def _strip_whitespace(obj: object) -> object:
    if isinstance(obj, str):
        return obj.strip()
    return obj  # pragma: no cover


StripWhitespace = BeforeValidator(func=_strip_whitespace)


def validate_uuid(value: str) -> Result[UUID, None]:
    try:
        return Ok(UUID(value))
    except ValueError:
        return Err(None)
