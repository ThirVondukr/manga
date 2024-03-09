import dataclasses


@dataclasses.dataclass
class EntityAlreadyExistsError:
    pass


@dataclasses.dataclass
class NotFoundError:
    entity_id: str


@dataclasses.dataclass
class RelationshipNotFoundError:
    entity_id: str
    entity_name: str | None = None


@dataclasses.dataclass
class PermissionDeniedError:
    pass
