import strawberry

from lib.types import Language

LanguageGQL = strawberry.enum(Language, name="LanguageEnum")
