from typing import Literal

from result import Err, Ok, Result

from app.core.errors import PermissionDeniedError
from app.db.models import User


class PermissionService:
    async def is_superuser_check(
        self,
        user: User,
    ) -> Result[Literal[True], PermissionDeniedError]:
        if not user.is_superuser:
            return Err(PermissionDeniedError())

        return Ok(user.is_superuser)
