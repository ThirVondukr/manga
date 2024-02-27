import strawberry

from lib.types import Language, MangaStatus

LanguageGQL = strawberry.enum(Language, name="LanguageEnum")
MangaStatusGQL = strawberry.enum(MangaStatus, name="MangaStatus")
