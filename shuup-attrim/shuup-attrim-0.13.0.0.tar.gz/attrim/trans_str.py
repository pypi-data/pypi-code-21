from typing import Union, Iterable, Tuple, Dict, Optional
from decimal import Decimal

from django.utils.translation import get_language
from shuup_utils.lang_constants import LANG_CODES


LangCode = str
TransStrValue = str
TransStrDict = Dict[LangCode, str]


class TransStr(Iterable):
    """
    Wrapper for the values of a translated field.
    Ensures that the passed lang codes are present in `settings.LANGUAGES`.
    
    The most useful feature is the iteration, for example:
        lang_code, value in some_trans_str:
            pass
    """
    def __init__(self, **translations: TransStrValue):
        self._validate_lang_codes(lang_codes=translations.keys())
        self._translations = translations # type: TransStrDict

    def get_value_in_current_lang(self) -> Optional[TransStrValue]:
        lang_code_current = get_language()
        return self.get_value(lang_code_current)

    def as_dict(self) -> TransStrDict:
        """
        Useful for the rest api tests.
        """
        return self._translations

    def copy(self) -> 'TransStr':
        return TransStr(**self._translations)

    def get_value(self, lang_code: LangCode, default=None) -> Optional[TransStrValue]:
        value = self._translations.get(lang_code, default)
        if value == '':
            value = None
        return value

    def is_empty(self) -> bool:
        return self._translations == {}

    def _validate_lang_codes(self, lang_codes: Iterable[LangCode]):
        for lang_code_given in lang_codes:
            self._validate_lang_code(lang_code_given)

    def _validate_lang_code(self, lang_code: LangCode):
        if lang_code not in LANG_CODES:
            raise ValueError(
                'The language code `{}` is not defined in your django '
                'settings.LANGUAGES.'
                    .format(lang_code)
            )

    def __iter__(self) -> Iterable[Tuple[LangCode, TransStrValue]]:
        for lang_code, value in self._translations.items():
            yield lang_code, value

    def __getitem__(self, lang_code: LangCode) -> TransStrValue:
        return self._translations[lang_code]

    def __setitem__(self, lang_code: LangCode, value: TransStrValue):
        self._validate_lang_code(lang_code)
        self._translations[lang_code] = value

    def __contains__(self, lang_code: LangCode) -> bool:
        is_contains = lang_code in self._translations
        return is_contains

    def __str__(self) -> TransStrValue:
        return self.get_value_in_current_lang()


#: represents all valid data types for `Option.value`
OptionValue = Union[
    int,
    Decimal,
    str,
    TransStr,
]
