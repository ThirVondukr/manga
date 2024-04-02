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
    HasTimestamps,
    PkUUID,
)
from lib.types import Language

if TYPE_CHECKING:
    from app.db.models import ImageSet
    from app.db.models.manga import Manga


manga_art__image = Table(
    "manga_art__image",
    Base.metadata,
    Column(
        "manga_art_id",
        ForeignKey("manga_art.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "image_id",
        ForeignKey("image.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class MangaArt(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
    repr=False,
):
    __tablename__ = "manga_art"
    __table_args__ = (
        UniqueConstraint(
            "manga_id",
            "language",
            "volume",
            name="manga_art__manga_language_volume_uq",
        ),
    )

    volume: Mapped[int]
    language: Mapped[Language]

    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"), init=False)
    manga: Mapped[Manga] = relationship(
        back_populates="arts",
        default=None,
        foreign_keys=[manga_id],
    )
    image_set_id: Mapped[UUID] = mapped_column(
        ForeignKey("image_set.id"),
        init=False,
    )
    image_set: Mapped[ImageSet] = relationship()
