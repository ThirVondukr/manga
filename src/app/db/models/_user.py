from datetime import datetime
from uuid import UUID

from sqlalchemy import String, false
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column
from uuid_utils.compat import uuid7

from app.db import Base
from lib.time import utc_now


class User(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid7,
    )
    username: Mapped[str] = mapped_column(String(length=40), unique=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now)
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default=false(),
    )
