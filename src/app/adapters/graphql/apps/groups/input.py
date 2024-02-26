import strawberry

from app.core.domain.groups.dto import GroupCreateDTO


@strawberry.input(name="GroupCreateInput")
class GroupCreateInputGQL:
    name: str

    def to_dto(self) -> GroupCreateDTO:
        return GroupCreateDTO(
            name=self.name,
        )
