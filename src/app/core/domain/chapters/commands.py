from result import Err, Ok, Result

from app.core.domain.branches.repositories import BranchRepository
from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.domain.chapters.services import ChapterService
from app.core.errors import RelationshipNotFoundError
from app.db.models import MangaChapter, User


class ChapterCreateCommand:
    def __init__(
        self,
        chapter_service: ChapterService,
        branch_repository: BranchRepository,
    ) -> None:
        self._chapter_service = chapter_service
        self._branch_repository = branch_repository

    async def execute(
        self,
        dto: ChapterCreateDTO,
        user: User,
    ) -> Result[MangaChapter, RelationshipNotFoundError]:
        branch = await self._branch_repository.get(id=dto.branch_id)
        if branch is None:
            return Err(RelationshipNotFoundError(entity_id=str(dto.branch_id)))

        chapter = await self._chapter_service.create(
            dto=dto,
            user=user,
            branch=branch,
        )
        return Ok(chapter)
