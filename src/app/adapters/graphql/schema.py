import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from graphql import GraphQLError
from strawberry import Schema
from strawberry.enum import EnumDefinition, EnumValue
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import (
    AddValidationRules,
    MaskErrors,
    ParserCache,
    ValidationCache,
)
from strawberry.schema.config import StrawberryConfig
from strawberry.schema.name_converter import NameConverter
from strawberry.tools import merge_types

from app.adapters.graphql.apps.auth.mutation import AuthMutationsGQL
from app.adapters.graphql.apps.branches.mutations import MangaBranchMutationGQL
from app.adapters.graphql.apps.chapters.mutations import ChapterMutationGQL
from app.adapters.graphql.apps.chapters.query import ChaptersQuery
from app.adapters.graphql.apps.groups.mutation import GroupMutationsGQL
from app.adapters.graphql.apps.manga.mutation import MangaMutationsGQL
from app.adapters.graphql.apps.manga.query import MangaQuery
from app.adapters.graphql.apps.tags.query import TagsQueryGQL
from app.adapters.graphql.apps.users.query import UserQuery
from app.adapters.graphql.extensions import IsAuthenticated
from app.core.di import create_container
from lib.query_complexity import (
    QueryComplexityExtension,
    QueryComplexityValidationRule,
)

Query = merge_types(
    name="Query",
    types=(ChaptersQuery, MangaQuery, UserQuery, TagsQueryGQL),
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

    @strawberry.field
    async def branches(self) -> MangaBranchMutationGQL:
        return MangaBranchMutationGQL()

    @strawberry.field
    async def chapters(self) -> ChapterMutationGQL:
        return ChapterMutationGQL()


class CustomNameConverter(NameConverter):
    def from_enum_value(
        self,
        enum: EnumDefinition,  # noqa: ARG002
        enum_value: EnumValue,
    ) -> str:
        return enum_value.name.upper()


def _should_mask_error(error: GraphQLError) -> bool:
    if not isinstance(
        error.original_error,
        StrawberryGraphQLError,
    ):  # pragma: no cover
        return True
    return error.original_error.extensions != IsAuthenticated.error_extensions


schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(maxsize=128),
        ValidationCache(maxsize=128),
        QueryComplexityExtension(max_complexity=100, default_cost=1),
        AddValidationRules([QueryComplexityValidationRule]),
        MaskErrors(_should_mask_error),
        AioInjectExtension(container=create_container()),
    ],
    config=StrawberryConfig(name_converter=CustomNameConverter()),
)
