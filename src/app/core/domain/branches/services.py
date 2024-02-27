from app.core.domain.branches.dto import MangaBranchCreateDTO
from app.db.models import Manga, MangaBranch
from lib.db import DBContext


class MangaBranchService:
    def __init__(self, db_context: DBContext) -> None:
        self._db_context = db_context

    async def create(
        self,
        dto: MangaBranchCreateDTO,
        manga: Manga,
    ) -> MangaBranch:
        branch = MangaBranch(
            name=dto.name,
            language=dto.language,
            manga=manga,
        )
        self._db_context.add(branch)
        await self._db_context.flush()
        return branch
