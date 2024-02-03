import functools
import itertools
from collections.abc import Iterable
from typing import Any

import aioinject
from aioinject import Provider

from ._modules import database

modules: Iterable[Iterable[Provider[Any]]] = [
    database.providers,
]


@functools.cache
def create_container() -> aioinject.Container:
    container = aioinject.Container()

    for provider in itertools.chain.from_iterable(modules):
        container.register(provider)

    return container
