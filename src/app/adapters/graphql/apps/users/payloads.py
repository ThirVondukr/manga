from typing import Annotated

import strawberry

from app.adapters.graphql.apps.users.types import PrivateUserGQL
from app.adapters.graphql.errors import FileUploadErrorGQL

UserAvatarChangeError = Annotated[
    FileUploadErrorGQL,
    strawberry.union(name="UserAvatarChangeError"),
]


@strawberry.type(name="UserAvatarChangePayload")
class UserAvatarChangePayload:
    user: PrivateUserGQL | None
    error: UserAvatarChangeError | None
