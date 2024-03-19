from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
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
)

if TYPE_CHECKING:
    from app.db.models import User
    from app.db.models.manga import Manga


class MangaRating(HasTimestamps, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_rating"
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 and rating <= 10",
            "valid_rating_range_check",
        ),
    )

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        primary_key=True,
        init=False,
    )
    manga: Mapped[Manga] = relationship()
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
        init=False,
    )
    user: Mapped[User] = relationship()
    rating: Mapped[int]
