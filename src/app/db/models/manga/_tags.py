from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.core.domain.types import TagCategory
from app.db import Base
from app.db._base import (
    PkUUID,
)

if TYPE_CHECKING:
    from app.db.models.manga import Manga

manga_manga_tag_secondary_table = Table(
    "manga__manga_tag__secondary",
    Base.metadata,
    Column(
        "manga_id",
        ForeignKey("manga.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("manga_tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class MangaTag(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_tag"

    name: Mapped[str] = mapped_column(String(32), unique=True)
    name_slug: Mapped[str] = mapped_column(String(32), unique=True)
    manga: Mapped[list[Manga]] = relationship(
        secondary=manga_manga_tag_secondary_table,
        back_populates="tags",
        default_factory=list,
        repr=False,
    )
    category: Mapped[TagCategory]
