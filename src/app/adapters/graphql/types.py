from typing import TYPE_CHECKING, TypeVar

import strawberry
from starlette.datastructures import UploadFile
from strawberry.file_uploads import Upload

from app.db.models.manga import MangaBookmarkStatus
from lib.sort import SortDirection
from lib.types import Language, MangaStatus

T = TypeVar("T")

LanguageGQL = strawberry.enum(Language, name="LanguageEnum")
MangaStatusGQL = strawberry.enum(MangaStatus, name="MangaStatus")
SortDirectionGQL = strawberry.enum(SortDirection, name="SortDirection")

if TYPE_CHECKING:
    GraphQLFile = UploadFile
else:
    GraphQLFile = Upload

MangaBookmarkStatusGQL = strawberry.enum(
    MangaBookmarkStatus,
    name="MangaBookmarkStatus",
)
