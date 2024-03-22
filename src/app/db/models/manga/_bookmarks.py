from __future__ import annotations

import enum
from datetime import datetime
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
from app.db._types import IntEnumType
from lib.time import utc_now

if TYPE_CHECKING:
    from app.db.models import User
    from app.db.models.manga import Manga


class MangaBookmarkStatus(enum.IntEnum):
    plan_to_read = 0
    reading = 1
    completed = 2
    dropped = 4


class MangaBookmark(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_bookmark"

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        primary_key=True,
        init=False,
    )
    manga: Mapped[Manga] = relationship(lazy="raise")
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
        init=False,
    )
    status: Mapped[MangaBookmarkStatus] = mapped_column(
        IntEnumType(MangaBookmarkStatus),
    )
    user: Mapped[User] = relationship(lazy="raise")
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now)
