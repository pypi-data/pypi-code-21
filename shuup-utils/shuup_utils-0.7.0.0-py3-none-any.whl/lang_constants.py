from typing import List

from django.conf import settings


# 'en', 'fr', 'fi', etc
LangCode = str


def _get_languages_list() -> List[LangCode]:
    lang_codes = []
    for lang in settings.LANGUAGES:
        lang_codes.append(lang[0])
    return lang_codes


DEFAULT_LANG = settings.PARLER_DEFAULT_LANGUAGE_CODE  # type: LangCode

LANG_CODES = _get_languages_list()
