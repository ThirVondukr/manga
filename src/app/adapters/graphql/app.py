from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL

from app.core.di import create_container
from app.core.domain.auth.commands import AuthenticateAccessTokenCommand
from app.core.domain.auth.dto import TokenClaims
from lib.loaders import Dataloaders

from .context import Context
from .schema import schema


class GraphQLApp(GraphQL[Context, None]):
    async def get_context(
        self,
        request: Request | WebSocket,
        response: Response | None = None,
    ) -> Context:
        claims = await self._authenticate_user(request=request)
        return Context(
            request=request,
            response=response,
            loaders=Dataloaders(),
            maybe_access_token=claims,
        )

    async def _authenticate_user(
        self,
        request: Request | WebSocket,
    ) -> TokenClaims | None:
        token = request.headers.get("authorization", "")
        async with create_container().context() as ctx:
            command = await ctx.resolve(AuthenticateAccessTokenCommand)
            return await command.execute(token=token)


def create_graphql_app() -> GraphQL[Context, None]:
    return GraphQLApp(
        schema=schema,
    )
