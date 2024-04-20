from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, false
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from uuid_utils.compat import uuid7

from app.db import Base
from app.db.models import ImageSet
from lib.time import utc_now


class User(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid7,
    )
    username: Mapped[str] = mapped_column(String(length=40), unique=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now)
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default=false(),
    )
    avatar_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("image_set.id"),
        default=None,
    )
    avatar: Mapped[ImageSet | None] = relationship(default=None)
