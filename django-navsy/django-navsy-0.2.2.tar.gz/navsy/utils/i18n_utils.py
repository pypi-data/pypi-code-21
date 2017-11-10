# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import translation

import re


def get_current_language():
    current_language = translation.get_language() or settings.LANGUAGE_CODE
    # print(current_language)
    return current_language


def call_function_for_language(func, language_code, args=None):
    # TODO: check if language code is in LANGUAGES
    current_language = get_current_language()
    language = language_code or current_language
    translation.activate(language)
    args = args or []
    result = func(*args)
    translation.activate(current_language)
    return result


def split_languages(languages_codes_str):
    return re.findall(r'[\w\-]+', languages_codes_str.lower()
                      ) if languages_codes_str else []
