import dataclasses


@dataclasses.dataclass
class EntityAlreadyExistsError:
    pass


@dataclasses.dataclass
class NotFoundError:
    entity_id: str


@dataclasses.dataclass
class RelationshipNotFoundError:
    entity_name: str
    entity_id: str
