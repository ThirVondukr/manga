from typing import final
from uuid import UUID

from sqlalchemy import select

from app.db.models import Image, ImageSet
from app.db.models.manga import MangaArt
from lib.loaders import SQLAListLoader, SQLALoader


@final
class ImageLoader(SQLALoader[UUID, Image]):
    column = Image.id
    stmt = select(Image)


@final
class MangaArtImagesLoader(SQLAListLoader[UUID, Image]):
    column = MangaArt.id
    stmt = (
        select(MangaArt.id, Image)
        .select_from(MangaArt)
        .join(MangaArt.image_set)
        .join(ImageSet.images)
        .order_by(Image.width.desc())
    )
