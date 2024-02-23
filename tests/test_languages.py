from app.db._base import RegConfigLanguage
from lib.types import Language


def test_language_enum_compat() -> None:
    for lang in Language:
        assert RegConfigLanguage[lang.name]

    for regconfig_lang in RegConfigLanguage:
        assert Language[regconfig_lang.name]
