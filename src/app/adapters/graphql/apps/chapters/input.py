from collections.abc import Sequence

import strawberry

from app.core.domain.manga.chapters.dto import ChapterCreateDTO
from lib.files import File


@strawberry.input(name="ChapterCreateInput")
class ChapterCreateInputGQL:
    title: str
    volume: int | None
    number: Sequence[int]

    branch_id: strawberry.ID

    def to_dto(self, pages: Sequence[File]) -> ChapterCreateDTO:
        return ChapterCreateDTO(
            title=self.title,
            volume=self.volume,
            number=self.number,
            pages=pages,
            branch_id=self.branch_id,  # type: ignore[arg-type]
        )
