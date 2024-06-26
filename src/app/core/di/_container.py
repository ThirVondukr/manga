import functools
import itertools
from collections.abc import Iterable
from typing import Any

import aioinject
from aioinject import Object, Provider
from pydantic_settings import BaseSettings

from app.settings import (
    AppSettings,
    AuthSettings,
    DatabaseSettings,
    ImageScaleSettings,
    ImageSettings,
    KeycloakSettings,
    S3Settings,
    SentrySettings,
)
from lib.settings import get_settings

from ._modules import (
    auth,
    database,
    groups,
    images,
    keycloak,
    manga,
    s3,
    users,
)

modules: Iterable[Iterable[Provider[Any]]] = [
    auth.providers,
    database.providers,
    groups.providers,
    images.providers,
    keycloak.providers,
    manga.providers,
    s3.providers,
    users.providers,
]

settings_classes: Iterable[type[BaseSettings]] = [
    AppSettings,
    AuthSettings,
    DatabaseSettings,
    ImageScaleSettings,
    ImageSettings,
    KeycloakSettings,
    S3Settings,
    SentrySettings,
]


@functools.cache
def create_container() -> aioinject.Container:
    container = aioinject.Container()

    for provider in itertools.chain.from_iterable(modules):
        container.register(provider)

    for settings_cls in settings_classes:
        container.register(Object(get_settings(settings_cls)))

    return container
