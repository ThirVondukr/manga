from result import Err, Ok, Result

from app.core.domain.groups.repositories import GroupRepository
from app.core.domain.manga.branches.dto import MangaBranchCreateDTO
from app.core.domain.manga.branches.services import MangaBranchService
from app.core.domain.manga.manga.repositories import MangaRepository
from app.core.errors import RelationshipNotFoundError
from app.db.models import MangaBranch, User


class MangaBranchCreateCommand:
    def __init__(
        self,
        manga_repository: MangaRepository,
        service: MangaBranchService,
        group_repository: GroupRepository,
    ) -> None:
        self._manga_repository = manga_repository
        self._group_repository = group_repository
        self._service = service

    async def execute(
        self,
        dto: MangaBranchCreateDTO,
        user: User,  # noqa: ARG002
    ) -> Result[MangaBranch, RelationshipNotFoundError]:
        if (manga := await self._manga_repository.get(id=dto.manga_id)) is None:
            return Err(
                RelationshipNotFoundError(
                    entity_name="Manga",
                    entity_id=str(dto.manga_id),
                ),
            )
        if (group := await self._group_repository.get(id=dto.group_id)) is None:
            return Err(
                RelationshipNotFoundError(
                    entity_name="MangaBranch",
                    entity_id=str(dto.group_id),
                ),
            )

        chapter = await self._service.create(dto=dto, manga=manga, group=group)
        return Ok(chapter)
