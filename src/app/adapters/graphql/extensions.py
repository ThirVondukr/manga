from typing import Any

from strawberry import BasePermission
from strawberry.permission import PermissionExtension

from app.adapters.graphql.context import Info


class IsAuthenticated(BasePermission):
    message = "Not Authenticated"
    error_extensions = {"code": "UNAUTHORIZED"}  # noqa: RUF012

    def has_permission(
        self,
        source: Any,  # noqa: ARG002, ANN401
        info: Info,
        **kwargs: Any,  # noqa: ARG002, ANN401
    ) -> bool:
        return info.context.maybe_access_token is not None


AuthExtension = PermissionExtension([IsAuthenticated()])
