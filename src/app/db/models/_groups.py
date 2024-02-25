from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.db import Base
from app.db._base import HasTimestamps, PkUUID

if TYPE_CHECKING:
    from app.db.models import User


class Group(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(String(250))
    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        init=False,
    )
    created_by: Mapped[User] = relationship()
