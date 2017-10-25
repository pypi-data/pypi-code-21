import requests

BASE_URL = 'https://www.deepl.com/jsonrpc'

LANGUAGES = {
    'auto': 'Auto',
    'DE': 'German',
    'EN': 'English',
    'FR': 'French',
    'ES': 'Spanish',
    'IT': 'Italian',
    'NL': 'Dutch',
    'PL': 'Polish'
}

JSONRPC_VERSION = '2.0'
DEEPL_METHOD = 'LMT_handle_jobs'


class TranslationError(Exception):
    def __init__(self, message):
        super(TranslationError, self).__init__(message)


def translate(text, to_lang, from_lang='auto', json=False):
    if text is None:
        raise TranslationError('Text can\'t be None.')
    if len(text) > 5000:
        raise TranslationError('Text too long (limited to 5000 characters).')
    if to_lang not in LANGUAGES.keys():
        raise TranslationError('Language {} not available.'.format(to_lang))
    if from_lang is not None and from_lang not in LANGUAGES.keys():
        raise TranslationError('Language {} not available.'.format(from_lang))

    parameters = {
        'jsonrpc': JSONRPC_VERSION,
        'method': DEEPL_METHOD,
        'params': {
            'jobs': [
                {
                    'kind':'default',
                    'raw_en_sentence': text
                }
            ],
            'lang': {
                'user_preferred_langs': [
                    from_lang,
                    to_lang
                ],
                'source_lang_user_selected': from_lang,
                'target_lang': to_lang
            },
        },
    }

    response = requests.post(BASE_URL, json=parameters).json()

    if 'result' not in response:
        raise TranslationError('DeepL call resulted in a unknown result.')

    translations = response['result']['translations']

    if len(translations) == 0 \
            or translations[0]['beams'] is None \
            or translations[0]['beams'][0]['postprocessed_sentence'] is None:
        raise TranslationError('No translations found.')

    if json:
        return response
    return translations[0]['beams'][0]['postprocessed_sentence']
