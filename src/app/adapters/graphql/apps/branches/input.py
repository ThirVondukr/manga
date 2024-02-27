import strawberry

from app.adapters.graphql.types import LanguageGQL
from app.core.domain.branches.dto import MangaBranchCreateDTO


@strawberry.input(name="MangaBranchCreateInput")
class MangaBranchCreateInput:
    name: str
    language: LanguageGQL
    manga_id: strawberry.ID

    def to_dto(self) -> MangaBranchCreateDTO:
        return MangaBranchCreateDTO(
            name=self.name,
            language=self.language,
            manga_id=self.manga_id,  # type: ignore[arg-type]
        )
