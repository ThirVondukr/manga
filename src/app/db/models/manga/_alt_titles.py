from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
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
    from app.db.models.manga import Manga


class AltTitle(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_alt_title"
    __table_args__ = (
        Index(
            "ix_manga_alt_title_pgroonga",
            "title",
            postgresql_using="pgroonga",
        ),
    )

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        index=True,
        default=None,
    )
    manga: Mapped[Manga] = relationship(
        back_populates="alt_titles",
        default=None,
    )
    language: Mapped[Language]
    title: Mapped[str] = mapped_column(String(250))
