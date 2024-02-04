import dataclasses


@dataclasses.dataclass(kw_only=True, slots=True)
class UserFilter:
    username: str | None = None
    email: str | None = None
