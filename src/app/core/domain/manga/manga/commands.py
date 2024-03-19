from result import Err, Result

from app.core.domain.manga.manga.dto import MangaCreateDTO, MangaUpdateDTO
from app.core.domain.manga.manga.repositories import MangaRepository
from app.core.domain.manga.manga.services import MangaPermissions, MangaService
from app.core.errors import (
    EntityAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.models import User
from app.db.models.manga import Manga


class MangaCreateCommand:
    def __init__(
        self,
        manga_service: MangaService,
        permissions: MangaPermissions,
    ) -> None:
        self._manga_service = manga_service
        self._permissions = permissions

    async def execute(
        self,
        dto: MangaCreateDTO,
        user: User,
    ) -> Result[Manga, EntityAlreadyExistsError | PermissionDeniedError]:
        if isinstance(
            permission_check := await self._permissions.can_create(
                user=user,
            ),
            Err,
        ):
            return permission_check

        return await self._manga_service.create(dto=dto)


class MangaUpdateCommand:
    def __init__(
        self,
        manga_service: MangaService,
        manga_repository: MangaRepository,
        permissions: MangaPermissions,
    ) -> None:
        self._manga_service = manga_service
        self._manga_repository = manga_repository
        self._permissions = permissions

    async def execute(
        self,
        dto: MangaUpdateDTO,
        user: User,
    ) -> Result[
        Manga,
        EntityAlreadyExistsError | NotFoundError | PermissionDeniedError,
    ]:
        if not (manga := await self._manga_repository.get(id=dto.id)):
            return Err(NotFoundError(entity_id=str(dto.id)))

        if isinstance(
            permission_check := await self._permissions.can_edit(
                user=user,
                manga=manga,
            ),
            Err,
        ):
            return permission_check

        return await self._manga_service.update(dto=dto, manga=manga)
