# -*- coding: utf-8 -*-
from pynlple.module import abs_path
from pynlple.processing.dictionary import DictionaryLookUp, FileFolderTokenMapping, DictionaryBasedTagger
from pynlple.processing.text import ClassTokenFilter, TokenFilter
import re


class DictionaryStopwordsFilter(ClassTokenFilter):

    def __init__(self, stopwords_provider, prep=None):
        self.__stopwords_provider = stopwords_provider
        self.__dictionary = DictionaryLookUp(self.__stopwords_provider, preprocessing_method=prep)
        self.__tagger = DictionaryBasedTagger(self.__dictionary)
        super().__init__(self.__tagger)


class PunctuationFilter(DictionaryStopwordsFilter):
    """
    Dictionary-based punctuation filter. Uses punctuation from `data/punctuation.txt`.

    Example usage::

    >>> filter_ = PunctuationFilter()
    >>> filter_.filter('Some , tokens ! and . punctuation !'.split())
    ['Some', 'tokens', 'and', 'punctuation']

    """

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['punctuation.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class SpecialTagFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=str.lower):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['special_tags.txt'],
            data_folder=abs_path(__file__, 'data'),
            recursive=False)
        super().__init__(self.__stopwords_provider, prep)


class DefaultStopwordsFilter(DictionaryStopwordsFilter):

    def __init__(self, prep=None):
        self.__stopwords_provider = FileFolderTokenMapping(
            ['punctuation.txt', {'rus/pos': ['conjunctions.txt', 'particles.txt', 'prepositions.txt', 'pronouns.txt']}],
            data_folder=abs_path(__file__, 'data'),
            recursive=True)
        super().__init__(self.__stopwords_provider, prep)


class RegexFilter(TokenFilter):

    def __init__(self, regex):
        self.__regex = regex
        self.__pattern = re.compile(self.__regex)

    def filter(self, tokens):
        return list(filter(lambda t: not self.__pattern.match(t), tokens))


class NumberTokenFilter(RegexFilter):

    def __init__(self, num_regex=r'^[\d\.,\-:]+$'):
        super().__init__(num_regex)