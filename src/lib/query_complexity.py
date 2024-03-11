import dataclasses
from collections.abc import MutableMapping
from typing import Self

import strawberry
from graphql import (
    DocumentNode,
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLError,
    GraphQLField,
    GraphQLSchema,
    GraphQLUnionType,
    ValidationContext,
    ValidationRule,
)
from strawberry.extensions import FieldExtension, SchemaExtension
from strawberry.extensions.field_extension import SyncExtensionResolver
from strawberry.field import StrawberryField
from strawberry.schema.schema_converter import GraphQLCoreConverter
from strawberry.schema_directive import Location
from strawberry.types import Info


@strawberry.schema_directive(name="cost", locations=[Location.FIELD_DEFINITION])
class Cost:
    complexity: int
    multiplier: int | None = strawberry.UNSET


class QueryCost(FieldExtension):
    def __init__(self, complexity: int) -> None:
        self.complexity = complexity

    def apply(self, field: StrawberryField) -> None:
        field.directives.append(Cost(complexity=self.complexity))

    async def resolve_async(
        self,
        next_: SyncExtensionResolver,
        source: object,
        info: Info[object, object],
        **kwargs: object,
    ) -> object:
        return await next_(source, info, **kwargs)


def _find_cost_directive(node: GraphQLField) -> Cost | None:
    for extension in node.extensions.values():
        for directive in extension.directives:
            if isinstance(directive, Cost):
                return directive
    return None


_STRAWBERRY_KEY = GraphQLCoreConverter.DEFINITION_BACKREF


def _find_extension(schema: GraphQLSchema) -> "QueryComplexityExtension | None":
    strawberry_schema: strawberry.Schema = schema.extensions[_STRAWBERRY_KEY]
    for extension in strawberry_schema.extensions:
        if isinstance(extension, QueryComplexityExtension):
            return extension
    return None


@dataclasses.dataclass(kw_only=True, slots=True)
class FragmentLateEval:
    name: str


@dataclasses.dataclass(kw_only=True, slots=True)
class State:
    cost: Cost | None = None
    multiplier: int = 1
    complexity: int
    children: list["State | FragmentLateEval"] = dataclasses.field(
        default_factory=list,
    )

    @classmethod
    def from_cost(cls, cost: Cost | None, default_complexity: int) -> Self:
        if cost is None:
            return cls(
                cost=cost,
                complexity=default_complexity,
            )
        return cls(
            cost=cost,
            multiplier=(
                cost.multiplier  # type: ignore[arg-type]
                if cost.multiplier not in (None, strawberry.UNSET)
                else 1
            ),
            complexity=(
                cost.complexity
                if cost.complexity not in (None, strawberry.UNSET)
                else default_complexity
            ),
        )


class QueryComplexityValidationRule(ValidationRule):
    def __init__(self, context: ValidationContext) -> None:
        super().__init__(context)
        self.extension: QueryComplexityExtension = _find_extension(  # type: ignore[assignment]
            context.schema,
        )
        self._state: list[State] = []
        self._fragments: MutableMapping[str, State] = {}

    def _enter(self, state: State, *, contributes_to_cost: bool = True) -> None:
        if contributes_to_cost:
            self._state[-1].children.append(state)
        self._state.append(state)

    def _leave(self) -> State:
        return self._state.pop()

    def _resolve_complexity(self, state: State | FragmentLateEval) -> int:
        if isinstance(state, FragmentLateEval):
            state = self._fragments[state.name]

        children_cost = sum(self._resolve_complexity(c) for c in state.children)
        return state.multiplier * children_cost + state.complexity

    def enter_document(self, node: DocumentNode, *args: object) -> None:
        if self.extension is None:
            # Issue a warning?
            return self.BREAK  # type: ignore[unreachable]
        self._enter(State(cost=None, complexity=0), contributes_to_cost=False)
        return None

    def leave_document(self, node: DocumentNode, *args: object) -> None:
        state = self._leave()
        assert not self._state  # noqa: S101
        complexity = self._resolve_complexity(state)
        if complexity > self.extension.max_complexity:
            self.report_error(
                GraphQLError(
                    f"Complexity of {complexity} is greater than max complexity of {self.extension.max_complexity}",
                    extensions={
                        "QUERY_COMPLEXITY": {
                            "CURRENT": complexity,
                            "MAX": self.extension.max_complexity,
                        },
                    },
                ),
            )

    def enter_field(self, node: FieldNode, *args: object) -> None:
        type_ = self.context.get_parent_type()
        assert type_  # noqa: S101

        cost = None
        if (
            not isinstance(type_, GraphQLUnionType)
            and node.name.value in type_.fields
        ):
            node_definition = type_.fields[node.name.value]
            cost = _find_cost_directive(node_definition)

        self._enter(
            State.from_cost(
                cost=cost,
                default_complexity=self.extension.default_complexity,
            ),
        )

    def leave_field(self, node: FieldNode, *args: object) -> None:
        self._leave()

    def enter_fragment_definition(
        self,
        node: FragmentDefinitionNode,
        *_args: object,
    ) -> None:
        state = State(complexity=0)
        self._fragments[node.name.value] = state
        self._enter(state, contributes_to_cost=False)

    def leave_fragment_definition(
        self,
        node: FragmentDefinitionNode,
        *_args: object,
    ) -> None:
        self._leave()

    def enter_fragment_spread(
        self,
        node: FragmentSpreadNode,
        *_args: object,
    ) -> None:
        fragment = self.context.get_fragment(node.name.value)
        if not fragment:
            return

        self._state[-1].children.append(
            FragmentLateEval(name=fragment.name.value),
        )


class QueryComplexityExtension(SchemaExtension):
    def __init__(self, max_complexity: int, default_cost: int = 0) -> None:
        self.max_complexity = max_complexity
        self.default_complexity = default_cost
