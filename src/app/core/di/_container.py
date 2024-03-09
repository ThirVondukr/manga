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
    S3Settings,
    SentrySettings,
)
from lib.settings import get_settings

from ._modules import (
    auth,
    bookmarks,
    branches,
    chapters,
    database,
    groups,
    import_,
    manga,
    manga_chapters,
    s3,
    tags,
    users,
)

modules: Iterable[Iterable[Provider[Any]]] = [
    auth.providers,
    bookmarks.providers,
    branches.providers,
    chapters.providers,
    database.providers,
    groups.providers,
    import_.providers,
    manga.providers,
    manga_chapters.providers,
    s3.providers,
    tags.providers,
    users.providers,
]

settings_classes: Iterable[type[BaseSettings]] = [
    AuthSettings,
    DatabaseSettings,
    SentrySettings,
    S3Settings,
    AppSettings,
]


@functools.cache
def create_container() -> aioinject.Container:
    container = aioinject.Container()

    for provider in itertools.chain.from_iterable(modules):
        container.register(provider)

    for settings_cls in settings_classes:
        container.register(Object(get_settings(settings_cls)))

    return container
