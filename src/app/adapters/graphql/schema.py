import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry import Schema
from strawberry.enum import EnumDefinition, EnumValue
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.schema.config import StrawberryConfig
from strawberry.schema.name_converter import NameConverter
from strawberry.tools import merge_types

from app.adapters.graphql.apps.auth.mutation import AuthMutationsGQL
from app.adapters.graphql.apps.groups.mutation import GroupMutationsGQL
from app.adapters.graphql.apps.manga.mutation import MangaMutationsGQL
from app.adapters.graphql.apps.manga.query import MangaQuery
from app.adapters.graphql.apps.users.query import UserQuery
from app.core.di import create_container

Query = merge_types(
    name="Query",
    types=(MangaQuery, UserQuery),
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


class CustomNameConverter(NameConverter):
    def from_enum_value(
        self,
        enum: EnumDefinition,  # noqa: ARG002
        enum_value: EnumValue,
    ) -> str:
        return enum_value.name.upper()


schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(maxsize=128),
        ValidationCache(maxsize=128),
        AioInjectExtension(container=create_container()),
    ],
    config=StrawberryConfig(name_converter=CustomNameConverter()),
)
