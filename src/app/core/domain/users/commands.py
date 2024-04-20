from app.core.domain.users.services import UserService
from app.db.models import User
from lib.files import File


class ChangeUserAvatarCommand:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    async def execute(self, user: User, avatar: File) -> User:
        return await self._user_service.update_avatar(user=user, avatar=avatar)
