from result import Err, Result
from sqlalchemy.orm import joinedload

from app.core.domain.manga.branches.repositories import BranchRepository
from app.core.domain.manga.chapters.dto import ChapterCreateDTO
from app.core.domain.manga.chapters.services import ChapterService
from app.core.errors import (
    EntityAlreadyExistsError,
    PermissionDeniedError,
    RelationshipNotFoundError,
)
from app.db.models import MangaBranch, MangaChapter, User


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
    ) -> Result[
        MangaChapter,
        RelationshipNotFoundError
        | PermissionDeniedError
        | EntityAlreadyExistsError,
    ]:
        branch = await self._branch_repository.get(
            id=dto.branch_id,
            options=(joinedload(MangaBranch.manga),),
        )
        if branch is None:
            return Err(RelationshipNotFoundError(entity_id=str(dto.branch_id)))

        return await self._chapter_service.create(
            dto=dto,
            user=user,
            branch=branch,
        )
