from __future__ import annotations

from pathlib import PurePath

from sqlalchemy.orm import Mapped, MappedAsDataclass

from app.db import Base
from app.db._base import PkUUID


class Image(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "image"

    path: Mapped[PurePath]
    width: Mapped[int]
    height: Mapped[int]
