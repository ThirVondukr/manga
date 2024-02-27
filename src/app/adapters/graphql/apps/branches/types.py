from typing import Self

import strawberry

from app.adapters.graphql.dto import DTOMixin
from app.adapters.graphql.types import LanguageGQL
from app.db.models import MangaBranch


@strawberry.type(name="MangaBranch")
class MangaBranchGQL(DTOMixin[MangaBranch]):
    id: strawberry.ID
    name: str
    language: LanguageGQL

    @classmethod
    def from_dto(cls, model: MangaBranch) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            language=model.language,
        )
