# coding: utf-8

from __future__ import absolute_import

from django.utils.translation import get_language, get_language_info

# Taken from https://www.elastic.co/guide/en/elasticsearch/reference/2.2/analysis-lang-analyzer.html
# Django does not support some languages from the (e.g. Armenian and Sorani).
ELASTICSEARCH_LANGUAGE_ANALYZERS = (
    'arabic', 'armenian', 'basque', 'brazilian', 'bulgarian', 'catalan', 'cjk',
    'czech', 'danish', 'dutch', 'english', 'finnish', 'french', 'galician',
    'german', 'greek', 'hindi', 'hungarian', 'indonesian', 'irish', 'italian',
    'latvian', 'lithuanian', 'norwegian', 'persian', 'portuguese', 'romanian',
    'russian', 'sorani', 'spanish', 'swedish', 'turkish', 'thai',
)

DJANGO_COMPLEX_LANGUAGE_NAMES = ('brazilian', 'norwegian', 'spanish')


def get_elastic_language_analyzer():
    lang_code = get_language()
    lang_name = get_language_info(lang_code)['name'].lower()
    if lang_name in ELASTICSEARCH_LANGUAGE_ANALYZERS:
        return lang_name
    else:
        # cjk is Chinese, Japanese, and Korean
        if lang_name in ('japanese', 'korean') or 'chinese' in lang_name:
            return 'cjk'
        # for complex language names
        for complex_lang_name in DJANGO_COMPLEX_LANGUAGE_NAMES:
            if complex_lang_name in lang_name:
                return complex_lang_name
    # If matches not found return None so the engine will use default value


def get_whoosh_language_code():
    from whoosh.lang import two_letter_code
    lang_code = get_language()
    lang_name = get_language_info(lang_code)['name'].lower()
    return two_letter_code(lang_name)
