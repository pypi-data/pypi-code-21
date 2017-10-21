import re
import unicodedata

RE_COLOR_ANSI = re.compile(r'(\033\[[\d;]+m)')


# Borrow code from https://github.com/Robpol86/terminaltables
def visible_width(string):
    """Get the visible width of a unicode string.
    Some CJK unicode characters are more than one byte unlike
    ASCII and latin unicode characters.
    From: https://github.com/Robpol86/terminaltables/pull/9
    :param str string: String to measure.
    :return: String's width.
    :rtype: int
    """
    if '\033' in string:
        string = RE_COLOR_ANSI.sub('', string)

    # Convert to unicode.
    try:
        string = string.decode('u8')
    except (AttributeError, UnicodeEncodeError):
        pass

    width = 0
    for char in string:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1

    return width
