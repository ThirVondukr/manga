from uuid import UUID

from result import Err, Ok, Result


def validate_uuid(value: str) -> Result[UUID, None]:
    try:
        return Ok(UUID(value))
    except ValueError:
        return Err(None)
