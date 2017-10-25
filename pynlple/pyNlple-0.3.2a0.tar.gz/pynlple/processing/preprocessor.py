# -*- coding: utf-8 -*-
import re
import html

from pynlple.exceptions import TokenizationException


class IPreprocessor(object):
    """Interface to collect modules for text string preprocessing."""

    def preprocess(self, string_):
        return None


class Replacer(IPreprocessor):
    """Preprocessor interface for modules that replace certain text entities with normalized tags, etc."""


class StackingPreprocessor(IPreprocessor):
    """Class for continuous stacking and applying preprocessors in a natural order."""

    def __init__(self, preprocessor_list=None):
        if not preprocessor_list:
            self.preprocessors = []
        else:
            self.preprocessors = list(preprocessor_list)

    def append_preprocessor(self, preprocessor):
        self.preprocessors.append(preprocessor)

    def prepend_preprocessor(self, preprocessor):
        self.preprocessors.insert(0, preprocessor)

    def insert_preprocessor(self, position, preprocessor):
        self.preprocessors.insert(position, preprocessor)

    def preprocess(self, string_):
        out_string = string_
        for preprocessor in self.preprocessors:
            out_string = preprocessor.preprocess(out_string)
        return out_string


class ToLowerer(IPreprocessor):
    """Lowers all alpha characters."""

    def preprocess(self, string_):
        return string_.lower()


class RegexReplacer(Replacer):
    """Preprocessor. Replaces entities described by a specific regular expression from a text string
    with a stated string. Supports \n groups usage in target string."""

    def __init__(self, regex_query_string, target_string_with_groups, case_sensitive, use_locale, restrict_to_ascii):
        self.target = target_string_with_groups
        flag_1 = re.IGNORECASE if not case_sensitive else 0
        flag_2 = re.LOCALE if use_locale else 0
        flag_3 = re.ASCII if restrict_to_ascii else 0
        self.pattern = re.compile(regex_query_string, flag_1 | flag_2 | flag_3)
        super().__init__()

    def preprocess(self, string_):
        return re.sub(self.pattern, self.target, string_)


class RegexReplacerAdapter(RegexReplacer):

    def __init__(self, regex_query, replace_tag_with=None, case_sensitive=False, use_locale=False, restrict_to_ascii=False):
        if not replace_tag_with:
            replace_tag_with = ''
        super().__init__(regex_query, replace_tag_with, case_sensitive, use_locale, restrict_to_ascii)


class MultiWhitespaceReplacer(RegexReplacerAdapter):
    """Replace numerous whitespaces (\s+) in an input string with a default single space ' '."""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'\s+'
        super().__init__(regex_query, replace_tag_with)


class MultiNewLineReplacer(RegexReplacerAdapter):
    """Replace numerous newlines ([\r\n]+) in an input string with a default single newline '\r\n'."""

    def __init__(self, replace_tag_with='\r\n'):
        regex_query = r'[\r\n]+'
        super().__init__(regex_query, replace_tag_with)


class NewLineSpaceReplacer(RegexReplacerAdapter):
    """Replace numerous newlines ([\r\n]+) in an input string with a default single space ' '."""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'[\r\n]+'
        super().__init__(regex_query, replace_tag_with)


class MultiInLineWhitespaceReplacer(RegexReplacerAdapter):
    """Replace numerous in-line whitespaces ([\f   \t\v]+) in an input string with a default single space ' '.
    Note: there are 3 types of spaces as represented here: https://en.wikipedia.org/wiki/Punctuation"""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'[\f   \t\v]+'
        super().__init__(regex_query, replace_tag_with)


class Trimmer(Replacer):
    """Trims (or strips) heading and trailing whitespaces."""

    def preprocess(self, string_):
        return string_.strip()


class HtmlTagReplacer(RegexReplacerAdapter):
    """Replaces all tags of format <tag> and </tag> including tags with attributes and inner values: <a href='..'>."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'<.*?>'
        super().__init__(regex_query, replace_tag_with)


class VKMentionReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '[<id>|<name>]'."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'\[[\w_\-:]+\|.*\]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class AtReferenceReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '@<id>' (or '@<name>'?).
    This replacer finds only such entities which are separate words (start the line or
    have blank whitespace)"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'((?<=\s)|(?<=^))@[\w_-]+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class URLReplacer(RegexReplacerAdapter):
    """Research https://mathiasbynens.be/demo/url-regex and https://gist.github.com/dperini/729294
    Since we need to increase recall of link-a-like entities in text, we adopt the algorithm with
    some possible erroneous cases.
    I used regexp from https://mathiasbynens.be/demo/url-regex by @stephenhay
    and extended with ftps, www, wwwDDD prefixes, and "\" variant of slash ("/")"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'((ht|f)tps?:[\\/]+|www\d{0,3}\.)([.…]+|[^\s\\/$.?#].[^\s]*)'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class EmailReplacer(RegexReplacerAdapter):
    """Replaces all e-mail-like entities, non-latin including. Includes length check for each entity part."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'[\w0-9][\w0-9._%+-]{0,63}@(?:[\w0-9](?:[\w0-9-]{0,62}[\w0-9])?\.){1,8}[\w]{2,63}'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class UserWroteRuReplacer(RegexReplacerAdapter):
    """Replaces automatically generated sequences of citing found on forums. Grammar belike: <user> wrote <date?>:"""
# ((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?)?
    def __init__(self, replace_tag_with=None):
        regex_query = r'[^\s]+\s(\(\d\d\.\d\d\.\d\d\s\d\d:\d\d\)\s)?писал\((а|a)\)\s?((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?\s?)?:'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DigitsReplacer(RegexReplacerAdapter):
    """Replaces all series of digits."""

    def __init__(self, multi, replace_tag_with=None):
        regex_query = r'\d+' if multi else r'\d'
        super().__init__(regex_query, replace_tag_with, False)


class CommaReplacer(RegexReplacerAdapter):
    """Replaces variations of comma taken from https://en.wikipedia.org/wiki/Punctuation.
    Symbols replaced: [,،、] to the default ','. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = ","

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'[,،、]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class QuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of single qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble single quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ['`ʹʻʼʽ՚‘’‚‛′‵] to the
    default [']. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = '\''

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        # Some of the symbols are taken from other than punctuation.txt section
        regex_query = r'[\'`ʹʻʼʽ՚‘’‚‛′‵]'
        # This section does not contain quotes from not-punctuation.txt section
        # regex_query = r'[\'‘’‚‛′‵]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DoubleQuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of double qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble double quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ["«»ʺ“”„‟″‶] to the
    default [\"]. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = "\""

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'["«»ʺ“”„‟″‶]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DoubleQuotesEscaper(RegexReplacerAdapter):
    """Escapes the double qoutes symbol with the corresponding string tag"""

    DEFAULT_REPLACEMENT = "DQTS"

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'\"'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DashAndMinusReplacer(RegexReplacerAdapter):
    """Replaces variations of dash/minus (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble dash and minus and may be used in its function.
    So, take care when using this class. Symbols replaced: [-‐‑‒–—] to the
    default [-]. Please, ref to http://unicode-table.com to decode symbols."""

    def __init__(self, replace_tag_with='-'):
        regex_query = r'[-‐‑‒–—]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class SoftHyphenReplacer(RegexReplacerAdapter):
    """Removes soft hyphen."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[­]'
        super().__init__(regex_query, replace_tag_with, False)


class TripledotReplacer(RegexReplacerAdapter):
    """Replaces triple dot one-symbol expression with 3 separate fullstops."""

    def __init__(self, replace_tag_with='...'):
        regex_query = r'[…]'
        super().__init__(regex_query, replace_tag_with, False)


class BoldTagReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with=''):
        regex_query = r'</?b>'
        super().__init__(regex_query, replace_tag_with, False)


def __read_data_file(data_file_path):
    import io
    from pynlple.module import abs_path, append_paths
    data_path = abs_path(__file__, 'data')
    file_path = append_paths(data_path, data_file_path)
    with io.open(file_path, 'rt', encoding='utf-8') as file:
        return [symbol for symbol in file]


def __escape(list_chars):
    import re
    return [re.escape(char) for char in list_chars]


def __list(symbols):
    return ''.join(__escape(symbols))


def __or(symbols):
    return '|'.join(__escape(symbols))

PUNCTUATION = __list(__read_data_file('punctuation.txt'))
SPECIAL_SYMBOLS = __list(__read_data_file('special_symbols.txt'))
CURRENCY = __list(__read_data_file('currency.txt'))
OR_CURRENCY = __or(__read_data_file('currency.txt'))


class MultiPunctuationReplacer(RegexReplacerAdapter):
    """Replaces all multiple punctuation and special symbols (default keyboard set + some additional:
    ref to data/punctuation.txt, data/special_symbols.txt, data/currency.t) with single corresponding symbol."""

    def __init__(self, replace_tag_with='\\1'):
        regex_query = r'([' + PUNCTUATION + SPECIAL_SYMBOLS + CURRENCY + r'])\1+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class NonWhitespaceAlphaNumPuncSpecSymbolsAllUnicodeReplacer(RegexReplacerAdapter):
    """Removes all unicode NON alpha-numeric, punctuation and special symbols (default keyboard set + some additional:
    ref to data/punctuation.txt, data/special_symbols.txt, data/currency.txt) and whitespaces."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[^\s\w' + PUNCTUATION + SPECIAL_SYMBOLS + CURRENCY + ']'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class NonWordOrNumberOrWhitespaceAllUnicodeReplacer(RegexReplacerAdapter):
    """This cannot handle _ correctly. This also cannot handle soft hyphen correctly."""

    def __init__(self, replace_tag_with=' '):
        parts = [
            r'(?<=\d)[,:\.](?!\d)|(?<!\d)[,:\.](?=\d)|(?<!\d)[,:\.](?!\d)',  # this leaves out digital sequences with , : . in middle
            r'(?<=[\w\d])[\'\-](?![\w\d])|(?<![\w\d])[\'\-](?=[\w\d])|(?<![\w\d])[\'\-](?![\w\d])',  # this leaves out alphanumeric tokens with - and ' in middle
            r'[^\s\w\d\'\-,:\.]+',  # all other non-whitespace, non-alpha and non-digits
            r'_',
            ]
        regex_query = r'(' + r'|'.join(parts) + r')+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class WordTokenizer(RegexReplacerAdapter):
    """"""

    TOKEN_DEFAULT_DELIM = ' '

    def __init__(self, token_delim=TOKEN_DEFAULT_DELIM):
        token_types = [
            r'([^\W\d_]+([\'\-][^\W\d_]+)*[^\W\d_]*)',  # tokens, also with - and ' in middle
            r'([^\W_]+([\'\-][^\W\d_]+)+)',  # tokens, starting with number and ' - in middle ("7-fold", etc.)
            r'(\d+([,:.]\d+)*\d*)',  # digital sequences, also with , : . in middle
            # r'[^\W\d_]+',  # all other alpha tokens, excluding underscore
            # r'[\d\W]+',  # all other numeric sequences
            r'\.+',
            r'[^\w\d\s]',  # all individual symbols that are not alphanum or whitespaces
            r'_',  # underscore as being exluded by \w and previously by [^\W\d_]+
            r'\r\n?',
        ]
        regex_query = r'(' + r'|'.join(token_types) + r')'
        super().__init__(regex_query, token_delim, False, False, False)

    def preprocess(self, string_):
        res = []
        for matches in re.finditer(self.pattern, string_):
            # sorted_groups = sorted(matches.groups(), key=lambda g: len(g) if g else 0, reverse=True)
            # res.append(sorted_groups[0])
            # filtered = filter(lambda m: m.end() - m.start() != 0, matches)
            # if len(filtered) > 1:
            #     raise TokenizationException(__name__ + ' regex yielded multiple tokenization: ' + ','.join(filtered))
            # match = filtered[0]
            if matches.span()[1] - matches.span()[0] < 0:
                raise TokenizationException(__name__ + ' regex yielded incorrect tokenization:\r\n'
                                            + 'string:"' + string_
                                            + '", span:[' + str(matches.span()[0])
                                            + ',' + str(matches.span()[1]) + '], results:"'
                                            + ','.join(res) + '"')
            res.append(matches.string[matches.span()[0]:matches.span()[1]])
        return WordTokenizer.TOKEN_DEFAULT_DELIM.join(res)


class HtmlEntitiesEscaper(Replacer):

    def preprocess(self, string_):
        return html.escape(string_)


class HtmlEntitiesUnescaper(Replacer):

    def preprocess(self, string_):
        return html.unescape(string_)


class PhoneNumberReplacer(RegexReplacerAdapter):
    """Replaces the phone-number-looking entities."""

    def __init__(self, replace_tag_with=' phoneNumTag '):
        regex_query = r'(?<!\d)(\+?\d{1,3})?[ ]?\(?\d{3,4}[\)-]?[ ]?\d{2,3}[ -]?[\d\- ]{4,5}(?!\d)'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class PriceReplacer(RegexReplacerAdapter):
    """Replaces the money entities with a corresponding tag. Encircles the name of the currency."""

    def __init__(self, replace_tag_with=' moneyAmountTag '):
        regex_query = r'[\d.]+(\s)?(?:р|грн|руб|рублей|рубля|EUR|' + OR_CURRENCY + r')\s*[\s.]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DefaultPreprocessorStack(StackingPreprocessor):
    def __init__(self, preserve_newlines=True):
        self.preserve_nl = preserve_newlines
        stack = [
                                        HtmlEntitiesUnescaper(),
                                        BoldTagReplacer(),
                                        URLReplacer(' urlTag '),
                                        HtmlTagReplacer(' '),
                                        VKMentionReplacer(' vkMentionTag '),
                                        EmailReplacer(' emailTag '),
                                        PhoneNumberReplacer(' phoneNumberTag '),
                                        AtReferenceReplacer(' atRefTag '),
                                        UserWroteRuReplacer(' userWroteRuTag '),
                                        CommaReplacer(),
                                        QuotesReplacer(),
                                        DoubleQuotesReplacer(),
                                        SoftHyphenReplacer(),
                                        DashAndMinusReplacer(),
                                        TripledotReplacer(),
                                        NonWhitespaceAlphaNumPuncSpecSymbolsAllUnicodeReplacer(''),
                                        ToLowerer(),
                                        DigitsReplacer(False, '0'),
                                        MultiPunctuationReplacer(),
                                        MultiNewLineReplacer(), MultiInLineWhitespaceReplacer() if self.preserve_nl else MultiWhitespaceReplacer(),
                                        # MultiWhitespaceReplacer() if not self.preserve_nl,
                                        # MultiNewLineReplacer() if not self.preserve_nl,
                                        WordTokenizer(),
                                        Trimmer(),
                                        # Any other?
        ]
        super().__init__(stack)


class ExtendedReplacerStack(DefaultPreprocessorStack):
    """
    Creates an extended (by appending to the end) instance of preprocessor.DefaultPreprocessorStack.

    @:param list list_extension_replacers: a list of preplacers to extend the default set with
    """
    def __init__(self, list_extension_replacers):
        super().__init__()
        self.extension_replacers = list_extension_replacers
        for replacer in self.extension_replacers:
            super().append_preprocessor(replacer)

