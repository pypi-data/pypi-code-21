# encoding: utf-8

import six
import inspect
import logging_helper

logging = logging_helper.setup_logging()

CONVERTER = u'converter'


def convert(value,
            converter,
            permitted_conversion_results=(u'', u'-', u'n/a', None),
            **kwargs):

    """
    Used to convert a value using the supplied conversion function

    :param value: value to convert
    :param converter: conversion function or a function dictionary
    :param permitted_conversion_results: a list of values that don't
                                         cause exceptions to be logged
    :param **kwargs parameter values for the converter function

    might be used for calling the function

       def epoch_to_time(ep = None,
                         format = u'%d-%m-%y %H:%M:%S')

    value is used as the the first parameter

        convert(value = datetime.now(),
                converter = epoch_to_time,
                format = u'%d-%m-%y')

    is equivalent to calling

        epoch_to_time(datetime.now(),
                    format = u'%d-%m-%y')

    """
    try:
        return converter(value,
                         **kwargs)
    except Exception as e:
        if value not in permitted_conversion_results:
            source = inspect.getsource(converter)
            logging.warning(u'Failed to convert value ({value}) '
                            u'using {function}. ({source})\n'
                            .format(value = value,
                                    function = converter,
                                    source = source))
            logging.exception(e)
    return value


def convert_to_unicode(source_string):
    return source_string if isinstance(source_string, unicode) else unicode(source_string)


FULL_WIDTH_TABLE = {u' ':      {u'code': u'U+3000', u'wide char': u"\u3000",  u'name': u'IDEOGRAPHIC SPACE'},
                    u'!':      {u'code': u'U+FF01', u'wide char': u'！',      u'name': u'FULLWIDTH EXCLAMATION MARK'},
                    u'"':      {u'code': u'U+FF02', u'wide char': u'＂',      u'name': u'FULLWIDTH QUOTATION MARK'},
                    u'#':      {u'code': u'U+FF03', u'wide char': u'＃',      u'name': u'FULLWIDTH NUMBER SIGN'},
                    u'$':      {u'code': u'U+FF04', u'wide char': u'＄',      u'name': u'FULLWIDTH DOLLAR SIGN'},
                    u'%':      {u'code': u'U+FF05', u'wide char': u'％',      u'name': u'FULLWIDTH PERCENT SIGN'},
                    u'&':      {u'code': u'U+FF06', u'wide char': u'＆',      u'name': u'FULLWIDTH AMPERSAND'},
                    u"'":      {u'code': u'U+FF07', u'wide char': u'＇',      u'name': u'FULLWIDTH APOSTROPHE'},
                    u'(':      {u'code': u'U+FF08', u'wide char': u'（',      u'name': u'FULLWIDTH LEFT PARENTHESIS'},
                    u')':      {u'code': u'U+FF09', u'wide char': u'）',      u'name': u'FULLWIDTH RIGHT PARENTHESIS'},
                    u'*':      {u'code': u'U+FF0A', u'wide char': u'＊',      u'name': u'FULLWIDTH ASTERISK'},
                    u'+':      {u'code': u'U+FF0B', u'wide char': u'＋',      u'name': u'FULLWIDTH PLUS SIGN'},
                    u',':      {u'code': u'U+FF0C', u'wide char': u'，',      u'name': u'FULLWIDTH COMMA'},
                    u'-':      {u'code': u'U+FF0D', u'wide char': u'－',      u'name': u'FULLWIDTH HYPHEN-MINUS'},
                    u'.':      {u'code': u'U+FF0E', u'wide char': u'．',      u'name': u'FULLWIDTH FULL STOP'},
                    u'/':      {u'code': u'U+FF0F', u'wide char': u'／',      u'name': u'FULLWIDTH SOLIDUS'},
                    u'0':      {u'code': u'U+FF10', u'wide char': u'０',      u'name': u'FULLWIDTH DIGIT ZERO'},
                    u'1':      {u'code': u'U+FF11', u'wide char': u'１',      u'name': u'FULLWIDTH DIGIT ONE'},
                    u'2':      {u'code': u'U+FF12', u'wide char': u'２',      u'name': u'FULLWIDTH DIGIT TWO'},
                    u'3':      {u'code': u'U+FF13', u'wide char': u'３',      u'name': u'FULLWIDTH DIGIT THREE'},
                    u'4':      {u'code': u'U+FF14', u'wide char': u'４',      u'name': u'FULLWIDTH DIGIT FOUR'},
                    u'5':      {u'code': u'U+FF15', u'wide char': u'５',      u'name': u'FULLWIDTH DIGIT FIVE'},
                    u'6':      {u'code': u'U+FF16', u'wide char': u'６',      u'name': u'FULLWIDTH DIGIT SIX'},
                    u'7':      {u'code': u'U+FF17', u'wide char': u'７',      u'name': u'FULLWIDTH DIGIT SEVEN'},
                    u'8':      {u'code': u'U+FF18', u'wide char': u'８',      u'name': u'FULLWIDTH DIGIT EIGHT'},
                    u'9':      {u'code': u'U+FF19', u'wide char': u'９',      u'name': u'FULLWIDTH DIGIT NINE'},
                    u':':      {u'code': u'U+FF1A', u'wide char': u'：',      u'name': u'FULLWIDTH COLON'},
                    u';':      {u'code': u'U+FF1B', u'wide char': u'；',      u'name': u'FULLWIDTH SEMICOLON'},
                    u'<':      {u'code': u'U+FF1C', u'wide char': u'＜',      u'name': u'FULLWIDTH LESS-THAN SIGN'},
                    u'=':      {u'code': u'U+FF1D', u'wide char': u'＝',      u'name': u'FULLWIDTH EQUALS SIGN'},
                    u'>':      {u'code': u'U+FF1E', u'wide char': u'＞',      u'name': u'FULLWIDTH GREATER-THAN SIGN'},
                    u'?':      {u'code': u'U+FF1F', u'wide char': u'？',      u'name': u'FULLWIDTH QUESTION MARK'},
                    u'@':      {u'code': u'U+FF20', u'wide char': u'＠',      u'name': u'FULLWIDTH COMMERCIAL AT'},
                    u'A':      {u'code': u'U+FF21', u'wide char': u'Ａ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER A'},
                    u'B':      {u'code': u'U+FF22', u'wide char': u'Ｂ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER B'},
                    u'C':      {u'code': u'U+FF23', u'wide char': u'Ｃ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER C'},
                    u'D':      {u'code': u'U+FF24', u'wide char': u'Ｄ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER D'},
                    u'E':      {u'code': u'U+FF25', u'wide char': u'Ｅ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER E'},
                    u'F':      {u'code': u'U+FF26', u'wide char': u'Ｆ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER F'},
                    u'G':      {u'code': u'U+FF27', u'wide char': u'Ｇ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER G'},
                    u'H':      {u'code': u'U+FF28', u'wide char': u'Ｈ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER H'},
                    u'I':      {u'code': u'U+FF29', u'wide char': u'Ｉ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER I'},
                    u'J':      {u'code': u'U+FF2A', u'wide char': u'Ｊ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER J'},
                    u'K':      {u'code': u'U+FF2B', u'wide char': u'Ｋ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER K'},
                    u'L':      {u'code': u'U+FF2C', u'wide char': u'Ｌ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER L'},
                    u'M':      {u'code': u'U+FF2D', u'wide char': u'Ｍ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER M'},
                    u'N':      {u'code': u'U+FF2E', u'wide char': u'Ｎ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER N'},
                    u'O':      {u'code': u'U+FF2F', u'wide char': u'Ｏ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER O'},
                    u'P':      {u'code': u'U+FF30', u'wide char': u'Ｐ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER P'},
                    u'Q':      {u'code': u'U+FF31', u'wide char': u'Ｑ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER Q'},
                    u'R':      {u'code': u'U+FF32', u'wide char': u'Ｒ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER R'},
                    u'S':      {u'code': u'U+FF33', u'wide char': u'Ｓ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER S'},
                    u'T':      {u'code': u'U+FF34', u'wide char': u'Ｔ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER T'},
                    u'U':      {u'code': u'U+FF35', u'wide char': u'Ｕ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER U'},
                    u'V':      {u'code': u'U+FF36', u'wide char': u'Ｖ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER V'},
                    u'W':      {u'code': u'U+FF37', u'wide char': u'Ｗ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER W'},
                    u'X':      {u'code': u'U+FF38', u'wide char': u'Ｘ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER X'},
                    u'Y':      {u'code': u'U+FF39', u'wide char': u'Ｙ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER Y'},
                    u'Z':      {u'code': u'U+FF3A', u'wide char': u'Ｚ',      u'name': u'FULLWIDTH LATIN CAPITAL LETTER Z'},
                    u'[':      {u'code': u'U+FF3B', u'wide char': u'［',      u'name': u'FULLWIDTH LEFT SQUARE BRACKET'},
                    u'\\':     {u'code': u'U+FF3C', u'wide char': u'＼',      u'name': u'FULLWIDTH REVERSE SOLIDUS'},
                    u']':      {u'code': u'U+FF3D', u'wide char': u'］',      u'name': u'FULLWIDTH RIGHT SQUARE BRACKET'},
                    u"\u0302": {u'code': u'U+FF3E', u'wide char': u'＾',      u'name': u'FULLWIDTH CIRCUMFLEX ACCENT'},
                    u'_':      {u'code': u'U+FF3F', u'wide char': u'＿',      u'name': u'FULLWIDTH LOW LINE'},
                    u"\u0060": {u'code': u'U+FF40', u'wide char': u'｀',      u'name': u'FULLWIDTH GRAVE ACCENT'},
                    u'a':      {u'code': u'U+FF41', u'wide char': u'ａ',      u'name': u'FULLWIDTH LATIN SMALL LETTER A'},
                    u'b':      {u'code': u'U+FF42', u'wide char': u'ｂ',      u'name': u'FULLWIDTH LATIN SMALL LETTER B'},
                    u'c':      {u'code': u'U+FF43', u'wide char': u'ｃ',      u'name': u'FULLWIDTH LATIN SMALL LETTER C'},
                    u'd':      {u'code': u'U+FF44', u'wide char': u'ｄ',      u'name': u'FULLWIDTH LATIN SMALL LETTER D'},
                    u'e':      {u'code': u'U+FF45', u'wide char': u'ｅ',      u'name': u'FULLWIDTH LATIN SMALL LETTER E'},
                    u'f':      {u'code': u'U+FF46', u'wide char': u'ｆ',      u'name': u'FULLWIDTH LATIN SMALL LETTER F'},
                    u'g':      {u'code': u'U+FF47', u'wide char': u'ｇ',      u'name': u'FULLWIDTH LATIN SMALL LETTER G'},
                    u'h':      {u'code': u'U+FF48', u'wide char': u'ｈ',      u'name': u'FULLWIDTH LATIN SMALL LETTER H'},
                    u'i':      {u'code': u'U+FF49', u'wide char': u'ｉ',      u'name': u'FULLWIDTH LATIN SMALL LETTER I'},
                    u'j':      {u'code': u'U+FF4A', u'wide char': u'ｊ',      u'name': u'FULLWIDTH LATIN SMALL LETTER J'},
                    u'k':      {u'code': u'U+FF4B', u'wide char': u'ｋ',      u'name': u'FULLWIDTH LATIN SMALL LETTER K'},
                    u'l':      {u'code': u'U+FF4C', u'wide char': u'ｌ',      u'name': u'FULLWIDTH LATIN SMALL LETTER L'},
                    u'm':      {u'code': u'U+FF4D', u'wide char': u'ｍ',      u'name': u'FULLWIDTH LATIN SMALL LETTER M'},
                    u'n':      {u'code': u'U+FF4E', u'wide char': u'ｎ',      u'name': u'FULLWIDTH LATIN SMALL LETTER N'},
                    u'o':      {u'code': u'U+FF4F', u'wide char': u'ｏ',      u'name': u'FULLWIDTH LATIN SMALL LETTER O'},
                    u'p':      {u'code': u'U+FF50', u'wide char': u'ｐ',      u'name': u'FULLWIDTH LATIN SMALL LETTER P'},
                    u'q':      {u'code': u'U+FF51', u'wide char': u'ｑ',      u'name': u'FULLWIDTH LATIN SMALL LETTER Q'},
                    u'r':      {u'code': u'U+FF52', u'wide char': u'ｒ',      u'name': u'FULLWIDTH LATIN SMALL LETTER R'},
                    u's':      {u'code': u'U+FF53', u'wide char': u'ｓ',      u'name': u'FULLWIDTH LATIN SMALL LETTER S'},
                    u't':      {u'code': u'U+FF54', u'wide char': u'ｔ',      u'name': u'FULLWIDTH LATIN SMALL LETTER T'},
                    u'u':      {u'code': u'U+FF55', u'wide char': u'ｕ',      u'name': u'FULLWIDTH LATIN SMALL LETTER U'},
                    u'v':      {u'code': u'U+FF56', u'wide char': u'ｖ',      u'name': u'FULLWIDTH LATIN SMALL LETTER V'},
                    u'w':      {u'code': u'U+FF57', u'wide char': u'ｗ',      u'name': u'FULLWIDTH LATIN SMALL LETTER W'},
                    u'x':      {u'code': u'U+FF58', u'wide char': u'ｘ',      u'name': u'FULLWIDTH LATIN SMALL LETTER X'},
                    u'y':      {u'code': u'U+FF59', u'wide char': u'ｙ',      u'name': u'FULLWIDTH LATIN SMALL LETTER Y'},
                    u'z':      {u'code': u'U+FF5A', u'wide char': u'ｚ',      u'name': u'FULLWIDTH LATIN SMALL LETTER Z'},
                    u'{':      {u'code': u'U+FF5B', u'wide char': u'｛',      u'name': u'FULLWIDTH LEFT CURLY BRACKET'},
                    u'|':      {u'code': u'U+FF5C', u'wide char': u'｜',      u'name': u'FULLWIDTH VERTICAL LINE'},
                    u'}':      {u'code': u'U+FF5D', u'wide char': u'｝',      u'name': u'FULLWIDTH RIGHT CURLY BRACKET'},
                    u'~':      {u'code': u'U+FF5E', u'wide char': u'～',      u'name': u'FULLWIDTH TILDE'},
                    u"¢":      {u'code': u'U+FFE0', u'wide char': u'￠',      u'name': u'FULLWIDTH CENT SIGN'},
                    u'£':      {u'code': u'U+FFE1', u'wide char': u'￡',      u'name': u'FULLWIDTH POUND SIGN'},
                    }


def convert_to_full_width_characters(string):
    for char in FULL_WIDTH_TABLE:
        string = string.replace(char,
                                FULL_WIDTH_TABLE[char][u'wide char'])
    return string


def dictify(*args,
            **kwargs):
    """
    Returns a simgle dictionary which is a combinations of all
    args and kwawrgs.

    :param args: all args must be dictionaries
    :param kwargs: the kwargs are added to the dictionary
    :return:
    """
    d = {}
    for arg in args:
        d.update(arg)
    d.update(kwargs)
    return d


class ASCIIfy(object):

    UNICODE_LOOKUP = {u'A': u'AÀÁÂÄÆÃÅĀ',
                      u'C': u'CĆČ',
                      u'E': u'EÈÉÊËĒĖĘ',
                      u'I': u'IÌĮĪÍÏÎ',
                      u'L': u'LŁ',
                      u'N': u'NŃÑ',
                      u'O': u'OÕŌØŒÓÒÖÔ',
                      u'S': u'SŚŠ',
                      u'U': u'UŪÚÙÜÛ',
                      u'W': u'WŴ',
                      u'Y': u'YŶ',
                      u'Z': u'ZŽŹŻ',

                      u'a': u'aàáâäæãåā',
                      u'c': u'cçćč',
                      u'e': u'eèéêëēėę',
                      u'i': u'iìįīíïî',
                      u'l': u'lł',
                      u'n': u'nńñ',
                      u'o': u'oõōøœóòöô',
                      u's': u'sßśš',
                      u'u': u'uūúùüû',
                      u'w': u'wŵ',
                      u'y': u'yŷ',
                      u'z': u'zžźż',
                      }

    PUNCTUATION_CHARS = (u"""`¬!"£$%^&*()_+-=[]{};'#:@~\,./|<>?""")

    def __init__(self):
        self.UNICODE_REVERSE_LOOKUP = {}

        for key, values in six.iteritems(self.UNICODE_LOOKUP):
            for value in values:
                self.UNICODE_REVERSE_LOOKUP[value] = key

    def asciify(self,
                term):
        return u''.join([self.UNICODE_REVERSE_LOOKUP.get(c, c)
                         for c in term])

    def replace_punctuation_char(self,
                                 c):
        return (u' '
                if c in self.PUNCTUATION_CHARS
                else c)

    def replace_punctuation(self,
                            term):
        return u''.join([self.replace_punctuation_char(c)
                         for c in term]).replace(u'  ',
                                                 u' ')

    def strip_punctuation(self,
                            term):
        return u''.join([c for c in term
                         if c not in self.PUNCTUATION_CHARS]).replace(u'  ', u' ')


