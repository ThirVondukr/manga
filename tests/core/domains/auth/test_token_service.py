from datetime import UTC, datetime

import freezegun
import pytest

from app.core.domain.auth.services import TokenService
from app.db.models import User
from app.settings import AuthSettings

pytestmark = pytest.mark.anyio


async def test_create_access_token_ok(
    user: User,
    now: datetime,
    token_service: TokenService,
    auth_settings: AuthSettings,
) -> None:
    now = now.replace(microsecond=0)
    with freezegun.freeze_time(now):
        result = token_service.create_access_token(user)

    claims = result.claims
    decoded_token = token_service.decode(result.token)

    assert (
        claims.token_type == decoded_token.token_type == "access"  # noqa: S105
    )
    assert claims.sub == decoded_token.sub == user.id
    assert (
        claims.exp.astimezone(UTC).replace(microsecond=0)
        == decoded_token.exp
        == (now + auth_settings.access_token_lifetime)
    )
    assert claims.iat == decoded_token.iat == now
