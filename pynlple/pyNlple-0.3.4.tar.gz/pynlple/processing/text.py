# -*- coding: utf-8 -*-


class WSTokenizer(object):

    def __init__(self, regex_query=r'[\f   \t\v]+'):
        import re
        self.__p = re.compile(regex_query)

    def tokenize(self, sentence):
        return self.__p.split(sentence)


class TokenTagger(object):

    def get_tagged_entities(self, tokens, all_=True):
        return None


class TokenFilter(object):

    def filter(self, tokens):
        """
        Filter out tokens according to specific rules.

        :param list tokens: string list of tokens to filter
        :return: filtered list of tokens
        :rtype: list
        """
        return None


class StackingFilter(TokenFilter):
    """Class for continuous stacking and applying filters in a natural order."""

    def __init__(self, filter_list=list()):
        self.filters = list(filter_list)

    def append_filter(self, filter):
        self.filters.append(filter)

    def prepend_filter(self, filter):
        self.filters.insert(0, filter)

    def filter(self, tokens):
        for filter in self.filters:
            tokens = filter.filter(tokens)
        return tokens


class ClassTokenFilter(TokenFilter):

    def __init__(self, tagger, filtered_classes=None):
        self.__tagger = tagger
        self.filtered_classes = filtered_classes

    def filter(self, tokens):
        tags = self.__tagger.get_tagged_entities(tokens, all_=False)
        if self.filtered_classes:
            tags = filter(lambda t: t[2] in self.filtered_classes, tags)
        valid_ids = sorted(set(range(0, len(tokens))) - {i for start, end, _ in tags for i in range(start, end)})
        return [tokens[i] for i in valid_ids]


