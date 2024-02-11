import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry import Schema
from strawberry.extensions import ParserCache, ValidationCache

from app.adapters.graphql.apps.auth.mutation import AuthMutationsGQL
from app.core.di import create_container


@strawberry.type
class Query:
    @strawberry.field
    async def hello_world(self) -> str:  # pragma: no cover
        return "Hello, World!"


@strawberry.type
class Mutation:
    @strawberry.field
    async def auth(self) -> AuthMutationsGQL:
        return AuthMutationsGQL()


schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(maxsize=128),
        ValidationCache(maxsize=128),
        AioInjectExtension(container=create_container()),
    ],
)
