from typing import TYPE_CHECKING

import strawberry
from starlette.datastructures import UploadFile
from strawberry.file_uploads import Upload

from lib.types import Language, MangaStatus

LanguageGQL = strawberry.enum(Language, name="LanguageEnum")
MangaStatusGQL = strawberry.enum(MangaStatus, name="MangaStatus")

if TYPE_CHECKING:
    GraphQLFile = UploadFile
else:
    GraphQLFile = Upload
