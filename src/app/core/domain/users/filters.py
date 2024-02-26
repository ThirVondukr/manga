import dataclasses
from uuid import UUID


@dataclasses.dataclass(kw_only=True, slots=True)
class UserFilter:
    id: UUID | None = None
    username: str | None = None
    email: str | None = None
