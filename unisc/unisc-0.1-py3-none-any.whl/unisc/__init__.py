"""Unicode Script Property """

import io
from os import path


UCD_VERSION = '10.0.0'

PROPERTY_VALUE_ALIASES_TXT = path.join(
    path.dirname(__file__), 'data', 'PropertyValueAliases.txt')
SCRIPTS_TXT = path.join(
    path.dirname(__file__), 'data', 'Scripts.txt')
SCRIPT_EXTENSIONS_TXT = path.join(
    path.dirname(__file__), 'data', 'ScriptExtensions.txt')


def abbr_name(name: str) -> str:
    """Return abbreviated ('Xxxx'-style) name for the Script property value.

    >>> abbr_name('Latin')
    'Latn'
    >>> abbr_name('Arabic')
    'Arab'
    >>> abbr_name('Katakana_Or_Hiragana')
    'Hrkt'
    >>> abbr_name('Inherited')
    'Zinh'
    >>> abbr_name('Common')
    'Zyyy'
    >>> abbr_name('Unknown')
    'Zzzz'
    """
    return _ABBR_NAMES[name]


def long_name(name: str) -> str:
    """Return long name for the Script property value.

    >>> long_name('Latn')
    'Latin'
    >>> long_name('Arab')
    'Arabic'
    >>> long_name('Hrkt')
    'Katakana_Or_Hiragana'
    >>> long_name('Zinh')
    'Inherited'
    >>> long_name('Zyyy')
    'Common'
    >>> long_name('Zzzz')
    'Unknown'
    """
    return _LONG_NAMES[name]


def script(uch: str) -> str:
    """Return Script property value of the code point.

    >>> script('\u0020')
    'Common'
    >>> script('\u0301')
    'Inherited'
    >>> script('\u243f')
    'Unknown'
    >>> script('\uffff')
    'Unknown'

    >>> script('\u0061')
    'Latin'
    >>> script('\u0363')
    'Inherited'
    >>> script('\u1cd1')
    'Inherited'

    >>> script('\u30fc')
    'Common'
    >>> script('\u3099')
    'Inherited'
    >>> script('\u1cd0')
    'Inherited'
    >>> script('\u1802')
    'Common'
    >>> script('\u060c')
    'Common'
    >>> script('\u0640')
    'Common'

    >>> script('\u096f')
    'Devanagari'
    >>> script('\u09ef')
    'Bengali'
    >>> script('\u1049')
    'Myanmar'
    """
    return _SCRIPT_PROPS.get(ord(uch), 'Unknown')


def script_extensions(uch: str) -> str:
    """Return Script_Extensions property value of the code point.

    >>> script_extensions('\u0020')
    ('Zyyy',)
    >>> script_extensions('\u0301')
    ('Zinh',)
    >>> script_extensions('\u243f')
    ('Zzzz',)
    >>> script_extensions('\uffff')
    ('Zzzz',)

    >>> script_extensions('\u0061')
    ('Latn',)
    >>> script_extensions('\u0363')
    ('Latn',)
    >>> script_extensions('\u1cd1')
    ('Deva',)

    >>> script_extensions('\u30fc')
    ('Hira', 'Kana')
    >>> script_extensions('\u3099')
    ('Hira', 'Kana')
    >>> script_extensions('\u1cd0')
    ('Deva', 'Gran')
    >>> script_extensions('\u1802')
    ('Mong', 'Phag')
    >>> script_extensions('\u060c')
    ('Arab', 'Syrc', 'Thaa')
    >>> script_extensions('\u0640')
    ('Adlm', 'Arab', 'Mand', 'Mani', 'Phlp', 'Syrc')

    >>> script_extensions('\u096f')
    ('Deva', 'Kthi', 'Mahj')
    >>> script_extensions('\u09ef')
    ('Beng', 'Cakm', 'Sylo')
    >>> script_extensions('\u1049')
    ('Cakm', 'Mymr', 'Tale')
    """
    return _SCRIPT_EXTENSIONS_PROPS.get(ord(uch), (abbr_name(script(uch)),))


def _tokenize(fobj: io.TextIOWrapper):
    """Parse a UCD text file and iterate tokens. """
    for para in fobj:
        # Strip comments
        if '#' in para:
            para = para[:para.index('#')]

        # Ignore empty lines
        para = para.strip()
        if not para:
            continue

        tokens = tuple(x.strip() for x in para.split(';'))
        yield tokens


def _parse_range(desc: str):
    """Parse range description in the UCD property text files. """
    if '..' in desc:
        start, end = desc.split('..')
        start = int(start, 16)
        end = int(end, 16)
    else:
        start = end = int(desc, 16)
    return range(start, end+1)


def _parse_property_value_aliases(fobj: io.TextIOWrapper):
    """Parse PropertyValueAlieases.txt. """
    abbr_names_dict = {}
    long_names_dict = {}
    for tokens in _tokenize(fobj):
        prop = tokens[0]
        if prop != 'sc':
            continue
        abbr_name_ = tokens[1]
        long_names = tokens[2:]
        long_names_dict[abbr_name_] = long_names[0]
        for long_name_ in long_names:
            abbr_names_dict.setdefault(long_name_, abbr_name_)

        globals()[abbr_name_] = abbr_name_

    return abbr_names_dict, long_names_dict


def _parse_scripts_txt(fobj: io.TextIOWrapper):
    """Parse Scripts.txt. """
    for key, value in _tokenize(fobj):
        for code_point in _parse_range(key):
            yield code_point, value


def _parse_script_extensions_txt(fobj: io.TextIOWrapper):
    """Parse ScriptExtensions.txt. """
    for key, value in _tokenize(fobj):

        for code_point in _parse_range(key):
            yield code_point, tuple(value.split())


_ABBR_NAMES, _LONG_NAMES \
    = _parse_property_value_aliases(open(PROPERTY_VALUE_ALIASES_TXT))
_SCRIPT_PROPS = dict(_parse_scripts_txt(open(SCRIPTS_TXT)))
_SCRIPT_EXTENSIONS_PROPS \
    = dict(_parse_script_extensions_txt(open(SCRIPT_EXTENSIONS_TXT)))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
