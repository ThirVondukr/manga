from typing import Annotated

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from result import Err

from app.adapters.graphql.apps.users.payloads import UserAvatarChangePayload
from app.adapters.graphql.apps.users.types import PrivateUserGQL
from app.adapters.graphql.context import Info
from app.adapters.graphql.errors import FileUploadErrorGQL
from app.adapters.graphql.extensions import AuthExtension
from app.adapters.graphql.types import GraphQLFile
from app.core.domain.users.commands import ChangeUserAvatarCommand
from lib.files import FileReader


@strawberry.type(name="UserMutations")
class UserMutationsGQL:
    @strawberry.mutation(extensions=[AuthExtension])  # type: ignore[misc]
    @inject
    async def change_avatar(
        self,
        avatar: GraphQLFile,
        info: Info,
        command: Annotated[ChangeUserAvatarCommand, Inject],
    ) -> UserAvatarChangePayload:
        reader = FileReader(max_size=5 * 1024 * 1024)
        file = await reader.read_one(file=avatar)
        if isinstance(file, Err):
            return UserAvatarChangePayload(  # pragma: no cover
                user=None,
                error=FileUploadErrorGQL.from_error(file.err_value),
            )

        user = await info.context.user
        user = await command.execute(user=user, avatar=file.ok_value)
        return UserAvatarChangePayload(
            user=PrivateUserGQL.from_dto(user),
            error=None,
        )
