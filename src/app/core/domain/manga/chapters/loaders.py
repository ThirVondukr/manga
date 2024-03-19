from uuid import UUID

from sqlalchemy import select

from app.db.models import Image
from app.db.models.manga import MangaChapter, MangaPage
from lib.loaders import SQLAListLoader, SQLALoader


class ChapterPagesLoader(SQLAListLoader[UUID, MangaPage]):
    column = MangaPage.chapter_id
    stmt = select(MangaPage.chapter_id, MangaPage).order_by(MangaPage.number)


class ChapterLoader(SQLALoader[UUID, MangaChapter | None]):
    column = MangaChapter.id
    stmt = select(MangaChapter)


class MangaPageImagesLoader(SQLAListLoader[UUID, Image]):
    column = MangaPage.id
    stmt = (
        select(MangaPage.id, Image)
        .select_from(MangaPage)
        .join(MangaPage.images)
        .order_by(Image.width.desc())
    )
