from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.db import Base
from app.db._base import (
    PkUUID,
)

if TYPE_CHECKING:
    from app.db.models import Image
    from app.db.models.manga import MangaChapter


manga_page__image = Table(
    "manga_page__image",
    Base.metadata,
    Column(
        "manga_page_id",
        ForeignKey("manga_page.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "image_id",
        ForeignKey("image.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class MangaPage(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_page"
    __table_args__ = (UniqueConstraint("chapter_id", "number"),)

    chapter_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga_chapter.id"),
        index=True,
        init=False,
    )
    chapter: Mapped[MangaChapter] = relationship(back_populates="pages")
    number: Mapped[int]
    images: Mapped[list[Image]] = relationship(secondary=manga_page__image)
