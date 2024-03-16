from typing import final
from uuid import UUID

from sqlalchemy import select

from app.db.models import Image
from lib.loaders import SQLALoader


@final
class ImageLoader(SQLALoader[UUID, Image]):
    column = Image.id
    stmt = select(Image)
