from result import Err, Ok, Result

from app.core.domain.branches.dto import MangaBranchCreateDTO
from app.core.domain.branches.services import MangaBranchService
from app.core.domain.manga.repositories import MangaRepository
from app.core.errors import RelationshipNotFoundError
from app.db.models import MangaBranch, User


class MangaBranchCreateCommand:
    def __init__(
        self,
        manga_repository: MangaRepository,
        service: MangaBranchService,
    ) -> None:
        self._manga_repository = manga_repository
        self._service = service

    async def execute(
        self,
        dto: MangaBranchCreateDTO,
        user: User,  # noqa: ARG002
    ) -> Result[MangaBranch, RelationshipNotFoundError]:
        manga = await self._manga_repository.get(id=dto.manga_id)
        if manga is None:
            return Err(
                RelationshipNotFoundError(
                    entity_name="Manga",
                    entity_id=str(dto.manga_id),
                ),
            )

        return Ok(await self._service.create(dto=dto, manga=manga))
