from typing import final
from uuid import UUID

from sqlalchemy import select

from app.db.models import (
    AltTitle,
    Manga,
    MangaTag,
    manga_manga_tag_secondary_table,
)
from lib.loaders import SQLAListLoader, SQLALoader


class MangaAltTitleLoader(SQLAListLoader[UUID, AltTitle]):
    column = AltTitle.manga_id
    stmt = select(AltTitle.manga_id, AltTitle).order_by(
        AltTitle.language,
        AltTitle.id,
    )


@final
class MangaLoader(SQLALoader[UUID, Manga]):
    column = Manga.id
    stmt = select(Manga)


class MangaTagLoader(SQLAListLoader[UUID, MangaTag]):
    column = manga_manga_tag_secondary_table.c.manga_id
    stmt = (
        select(
            manga_manga_tag_secondary_table.c.manga_id,
            MangaTag,
        )
        .join(
            manga_manga_tag_secondary_table,
            manga_manga_tag_secondary_table.c.tag_id == MangaTag.id,
        )
        .order_by(
            MangaTag.name_slug,
        )
    )
