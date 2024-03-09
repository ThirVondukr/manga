from result import Err, Ok, Result
from slugify import slugify

from app.core.errors import EntityAlreadyExistsError
from app.db.models import Manga
from lib.db import DBContext

from .dto import MangaCreateDTO
from .filters import MangaFindFilter
from .repositories import MangaRepository


class MangaService:
    def __init__(
        self,
        db_context: DBContext,
        repository: MangaRepository,
    ) -> None:
        self._db_context = db_context
        self._repository = repository

    async def create(
        self,
        dto: MangaCreateDTO,
    ) -> Result[Manga, EntityAlreadyExistsError]:
        manga = Manga(
            title=dto.title,
            title_slug=slugify(dto.title),
            status=dto.status,
        )
        if (
            await self._repository.find_one(
                MangaFindFilter(title=dto.title, title_slug=manga.title_slug),
            )
            is not None
        ):
            return Err(EntityAlreadyExistsError())

        self._db_context.add(manga)
        await self._db_context.flush()
        return Ok(manga)
