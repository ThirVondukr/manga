import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry import Schema
from strawberry.extensions import ParserCache, ValidationCache

from app.core.di import create_container


@strawberry.type
class Query:
    @strawberry.field
    async def hello_world(self) -> str:
        return "Hello, World!"


schema = Schema(
    query=Query,
    extensions=[
        ParserCache(maxsize=128),
        ValidationCache(maxsize=128),
        AioInjectExtension(container=create_container()),
    ],
)
