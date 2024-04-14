import contextlib
from collections.abc import AsyncIterator

from aioinject import Singleton

from app.settings import KeycloakSettings
from lib.connectors.keycloak import KeycloakClient
from lib.types import Providers


@contextlib.asynccontextmanager
async def _create_keycloak_client(
    settings: KeycloakSettings,
) -> AsyncIterator[KeycloakClient]:
    async with KeycloakClient.create(base_url=settings.base_url) as client:
        yield client


providers: Providers = [
    Singleton(_create_keycloak_client),
]
