import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry import Schema
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.tools import merge_types

from app.adapters.graphql.apps.auth.mutation import AuthMutationsGQL
from app.adapters.graphql.apps.groups.mutation import GroupMutationsGQL
from app.adapters.graphql.apps.manga.mutation import MangaMutationsGQL
from app.adapters.graphql.apps.manga.query import MangaQuery
from app.core.di import create_container

Query = merge_types(
    name="Query",
    types=(MangaQuery,),
)


@strawberry.type
class Mutation:
    @strawberry.field
    async def auth(self) -> AuthMutationsGQL:
        return AuthMutationsGQL()

    @strawberry.field
    async def manga(self) -> MangaMutationsGQL:
        return MangaMutationsGQL()

    @strawberry.field
    async def groups(self) -> GroupMutationsGQL:
        return GroupMutationsGQL()


schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(maxsize=128),
        ValidationCache(maxsize=128),
        AioInjectExtension(container=create_container()),
    ],
)
