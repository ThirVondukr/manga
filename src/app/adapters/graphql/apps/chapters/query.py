import strawberry
from result import Err

from app.adapters.graphql.apps.chapters.types import MangaChapterGQL
from app.adapters.graphql.context import Info
from app.core.domain.manga.chapters.loaders import ChapterLoader
from lib.validators import validate_uuid


@strawberry.type
class ChaptersQuery:

    @strawberry.field
    async def chapter(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MangaChapterGQL | None:
        chapter_id = validate_uuid(id)
        if isinstance(chapter_id, Err):
            return None

        chapter = await info.context.loaders.map(ChapterLoader).load(
            chapter_id.ok_value,
        )
        return MangaChapterGQL.from_dto_optional(chapter)
