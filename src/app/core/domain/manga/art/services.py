import asyncio
import contextlib
from pathlib import PurePath
from uuid import UUID

from result import Err, Ok, Result
from uuid_utils.compat import uuid7

from app.core.domain.images.services import ImageService
from app.core.domain.manga.art.dto import MangaArtAddDTO, MangaArtsAddDTO
from app.core.errors import EntityAlreadyExistsError, NotFoundError
from app.core.storage import FileUpload
from app.db.models import Image, Manga
from app.db.models._manga import MangaArt
from app.settings import ImagePaths
from lib.db import DBContext


class MangaArtService:
    def __init__(
        self,
        db_context: DBContext,
        image_service: ImageService,
    ) -> None:
        self._db_context = db_context
        self._image_service = image_service

    async def add_arts(
        self,
        manga: Manga,
        dto: MangaArtsAddDTO,
    ) -> Result[Manga, EntityAlreadyExistsError]:
        existing_volumes = [(art.language, art.volume) for art in manga.arts]
        if any(
            (art_dto.language, art_dto.volume) in existing_volumes
            for art_dto in dto.arts
        ):
            return Err(EntityAlreadyExistsError())

        async with contextlib.AsyncExitStack() as exit_stack:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self._upload_art(
                            manga_id=manga.id,
                            art_dto=art_dto,
                            exit_stack=exit_stack,
                        ),
                    )
                    for art_dto in dto.arts
                ]

            for art_dto, task in zip(dto.arts, tasks, strict=True):
                image, preview = task.result()
                art = MangaArt(
                    language=art_dto.language,
                    volume=art_dto.volume,
                    image=image,
                    preview_image=preview,
                )
                manga.arts.append(art)
            self._db_context.add(manga)
            await self._db_context.flush()

        return Ok(manga)

    async def _upload_art(
        self,
        manga_id: UUID,
        art_dto: MangaArtAddDTO,
        exit_stack: contextlib.AsyncExitStack,
    ) -> tuple[Image, Image]:
        upload = FileUpload(
            file=art_dto.image,
            path=PurePath(
                ImagePaths.manga_arts,
                str(manga_id),
                str(uuid7()),
            ).with_suffix(art_dto.image.filename.suffix),
        )
        return await exit_stack.enter_async_context(
            self._image_service.upload_image_with_preview(
                upload,
                max_width=400,
            ),
        )

    async def set_cover_art(
        self,
        manga: Manga,
        art_id: UUID | None,
    ) -> Result[Manga, NotFoundError]:
        art = None
        if art_id is not None:
            art = next((art for art in manga.arts if art.id == art_id), None)
            if art is None:
                return Err(NotFoundError(entity_id=str(art_id)))

        manga.cover_art = art
        self._db_context.add(manga)
        return Ok(manga)
