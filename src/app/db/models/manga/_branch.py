from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
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
    str_title,
)
from lib.types import Language

if TYPE_CHECKING:
    from app.db.models import Group
    from app.db.models.manga import Manga, MangaChapter


class MangaBranch(PkUUID, HasTimestamps, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_branch"

    name: Mapped[str_title]
    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"), init=False)
    manga: Mapped[Manga] = relationship(back_populates="branches")
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"), init=False)
    group: Mapped[Group] = relationship()

    language: Mapped[Language]

    chapters: Mapped[list[MangaChapter]] = relationship(
        back_populates="branch",
        default_factory=list,
        repr=False,
    )
