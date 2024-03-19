from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    ForeignKey,
    Integer,
    String,
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

if TYPE_CHECKING:
    from app.db.models import User
    from app.db.models.manga import MangaBranch, MangaPage


class MangaChapter(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_chapter"
    __table_args__ = (
        UniqueConstraint(
            "branch_id",
            "number",
            name="manga_chapter__branch_number_uq",
        ),
    )

    branch_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga_branch.id"),
        index=True,
        init=False,
    )
    branch: Mapped[MangaBranch] = relationship(back_populates="chapters")

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        init=False,
    )
    created_by: Mapped[User] = relationship()

    title: Mapped[str] = mapped_column(String(250))

    volume: Mapped[int | None]
    number: Mapped[Sequence[int]] = mapped_column(ARRAY(Integer))

    pages: Mapped[list[MangaPage]] = relationship(
        order_by="MangaPage.number",
        back_populates="chapter",
    )
