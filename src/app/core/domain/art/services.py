import contextlib
from pathlib import PurePath

from result import Err, Ok, Result
from uuid_utils.compat import uuid7

from app.core.domain.art.dto import MangaArtsAddDTO
from app.core.domain.images.services import ImageService
from app.core.errors import EntityAlreadyExistsError
from app.core.storage import FileUpload
from app.db.models import Manga
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
            for art_dto in dto.arts:
                upload = FileUpload(
                    buffer=art_dto.image.buffer,
                    path=PurePath(
                        ImagePaths.manga_arts,
                        str(manga.id),
                        str(uuid7()),
                    ).with_suffix(art_dto.image.filename.suffix),
                )
                image, preview = await exit_stack.enter_async_context(
                    self._image_service.upload_image_with_preview(
                        upload,
                        max_width=400,
                    ),
                )
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
