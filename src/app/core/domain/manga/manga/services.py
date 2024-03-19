from typing import Literal

from result import Err, Ok, Result
from slugify import slugify

from app.core.domain.users.services import PermissionService
from app.core.errors import EntityAlreadyExistsError, PermissionDeniedError
from app.db.models import User
from app.db.models.manga import Manga
from lib.db import DBContext

from .dto import MangaCreateDTO
from .filters import MangaFindFilter
from .repositories import MangaRepository


class MangaPermissions:
    def __init__(self, permissions: PermissionService) -> None:
        self._permissions = permissions

    async def can_create(
        self,
        user: User,
    ) -> Result[Literal[True], PermissionDeniedError]:
        return await self._permissions.is_superuser_check(user=user)

    async def can_edit(
        self,
        user: User,
        manga: Manga,  # noqa: ARG002
    ) -> Result[Literal[True], PermissionDeniedError]:
        return await self._permissions.is_superuser_check(user=user)


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
        if isinstance(
            check := await self._update_precondition(title=dto.title),
            Err,
        ):
            return check

        manga = Manga(
            title=dto.title,
            title_slug=self._slug(dto.title),
            description=dto.description,
            status=dto.status,
        )
        self._db_context.add(manga)
        return Ok(manga)

    async def update(
        self,
        dto: MangaCreateDTO,
        manga: Manga,
    ) -> Result[Manga, EntityAlreadyExistsError]:
        if isinstance(
            check := await self._update_precondition(title=dto.title),
            Err,
        ):
            return check

        manga.title = dto.title
        manga.title_slug = self._slug(dto.title)
        manga.description = dto.description
        manga.status = dto.status
        self._db_context.add(manga)
        await self._db_context.flush()
        return Ok(manga)

    async def _update_precondition(
        self,
        title: str,
    ) -> Result[None, EntityAlreadyExistsError]:
        if (
            await self._repository.find_any(
                MangaFindFilter(title=title, title_slug=self._slug(title)),
            )
            is not None
        ):
            return Err(EntityAlreadyExistsError())
        return Ok(None)

    @classmethod
    def _slug(cls, title: str) -> str:
        return slugify(title)
