import strawberry

from app.adapters.graphql.apps.users.types import PrivateUserGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.extensions import AuthExtension


@strawberry.type
class UserQuery:
    @strawberry.field(extensions=[AuthExtension])  # type: ignore[misc]
    async def me(self, info: Info) -> PrivateUserGQL:
        if info.context.maybe_access_token is None:  # pragma: no cover
            msg = "User is not authenticated"
            raise ValueError(msg)
        return PrivateUserGQL.from_dto(await info.context.user)
