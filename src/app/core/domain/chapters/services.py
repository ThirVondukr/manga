from pathlib import PurePath

from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.storage import FileUpload, ImageStorage
from app.db.models import MangaBranch, MangaChapter, MangaPage, User
from app.settings import Buckets
from lib.db import DBContext


class ChapterService:
    def __init__(
        self,
        db_context: DBContext,
        image_storage: ImageStorage,
    ) -> None:
        self._db_context = db_context
        self._image_storage = image_storage

    async def create(
        self,
        dto: ChapterCreateDTO,
        branch: MangaBranch,
        user: User,
    ) -> MangaChapter:
        chapter = MangaChapter(
            branch=branch,
            created_by=user,
            title=dto.title,
            volume=dto.volume,
            number=dto.number,
            pages=[],
        )
        files_to_upload = [
            FileUpload(
                path=PurePath(
                    f"{Buckets.chapter_images}/{branch.manga_id}/{chapter.id}/{number}{file.filename.suffix}",
                ),
                buffer=file.buffer,
            )
            for number, file in enumerate(dto.pages, start=1)
        ]
        async with self._image_storage.upload_context(files_to_upload) as files:
            chapter.pages = [
                MangaPage(image_path=path, number=number, chapter=chapter)
                for number, path in enumerate(files, start=1)
            ]
            self._db_context.add(chapter)
            await self._db_context.flush()
            return chapter
