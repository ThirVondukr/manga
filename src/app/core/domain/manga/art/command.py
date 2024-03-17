from result import Err, Result
from sqlalchemy.orm import selectinload

from app.core.domain.manga.art.dto import MangaArtsAddDTO, MangaSetCoverArtDTO
from app.core.domain.manga.art.services import MangaArtService
from app.core.domain.manga.manga.repositories import MangaRepository
from app.core.domain.manga.manga.services import MangaPermissions
from app.core.errors import (
    EntityAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.models import Manga, User


class AddArtsToMangaCommand:
    def __init__(
        self,
        repository: MangaRepository,
        service: MangaArtService,
        permissions: MangaPermissions,
    ) -> None:
        self._repository = repository
        self._service = service
        self._permissions = permissions

    async def execute(
        self,
        user: User,
        dto: MangaArtsAddDTO,
    ) -> Result[
        Manga,
        PermissionDeniedError | EntityAlreadyExistsError | NotFoundError,
    ]:
        manga = await self._repository.get(
            id=dto.manga_id,
            options=(selectinload(Manga.arts),),
        )
        if manga is None:
            return Err(NotFoundError(entity_id=str(dto.manga_id)))

        if isinstance(
            check := await self._permissions.can_edit(user=user, manga=manga),
            Err,
        ):
            return check

        return await self._service.add_arts(manga=manga, dto=dto)


class MangaSetCoverArtCommand:
    def __init__(
        self,
        repository: MangaRepository,
        service: MangaArtService,
        permissions: MangaPermissions,
    ) -> None:
        self._repository = repository
        self._service = service
        self._permissions = permissions

    async def execute(
        self,
        user: User,
        dto: MangaSetCoverArtDTO,
    ) -> Result[
        Manga,
        PermissionDeniedError | NotFoundError,
    ]:
        manga = await self._repository.get(
            id=dto.manga_id,
            options=(selectinload(Manga.arts),),
        )
        if manga is None:
            return Err(NotFoundError(entity_id=str(dto.manga_id)))

        if isinstance(
            check := await self._permissions.can_edit(user=user, manga=manga),
            Err,
        ):
            return check

        return await self._service.set_cover_art(manga=manga, art_id=dto.art_id)
