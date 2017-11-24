# -*- coding: utf-8 -*-
import logging
import io
import gzip
import bz2

from gensim.models.doc2vec import TaggedDocument
from pynlple.data.source import Source


class StackingSource(Source):

    logger = logging.getLogger(__name__)

    def __init__(self, list_sources, log=False):
        self.sources = list_sources
        self.log = log

    def __iter__(self):
        # if self.log:
            # self.logger.info('[%s] Corpus iterator %s started yielding elements.', str(self.__class__.__name__), repr(self))
        for i_, source in enumerate(self.sources):
            if self.log:
                self.logger.info('[%s] Corpus iterator started yielding elements from source (%d/%d): %s.',
                             str(self.__class__.__name__), i_, len(self.sources), repr(source))
            for item in source:
                yield item


class DeduplicatingFixedCacheSizeSource(Source):

    def __init__(self, source, cache_size=10000, refresh=False):
        self.source = source
        self.cache_size = cache_size
        self.refresh = refresh

    def __iter__(self):
        from collections import OrderedDict
        self.__cache = OrderedDict()
        stub = 0
        for entry in self.source:
            if entry in self.__cache:
                if self.refresh:
                    self.__cache.move_to_end(entry)
            else:
                self.__cache.__setitem__(entry, stub)
                if self.cache_size is not None:
                    while len(self.__cache) > self.cache_size:
                        self.__cache.popitem(last=False)
                yield entry


class JsonFieldSource(Source):

    def __init__(self, json_source, key, default=None):
        self.json = json_source
        self.key = key
        self.default = default

    def __iter__(self):
        for json_entry in self.json:
            if self.key in json_entry:
                yield json_entry[self.key]
            else:
                yield self.default


class FilteringSource(Source):

    def __init__(self, source, condition):
        self.source = source
        self.condition = condition

    def __iter__(self):
        for entry in self.source:
            if self.condition(entry):
                yield entry


class MappingSource(Source):

    def __init__(self, source, function):
        self.source = source
        self.function = function

    def __iter__(self):
        for entry in self.source:
            yield self.function(entry)


class SplittingSource(Source):

    def __init__(self, source, splitting_function):
        self.source = source
        self.function = splitting_function

    def __iter__(self):
        for entry in self.source:
            for item in self.function(entry):
                yield item


class DFsTaggedDocumentSource(Source):

    def __init__(self, dataframe_sources, text_column, tag_columns=None):
        self.sources = dataframe_sources
        self.text_column = text_column
        self.tag_columns = tag_columns
        super().__init__()

    def __iter__(self):
        for source in self.sources:
            return DFTaggedDocumentSource(source, self.text_column, self.tag_columns)


class DFTaggedDocumentSource(Source):

    def __init__(self, dataframe_source, text_column, tag_columns=None):
        self.source = dataframe_source
        self.text_column = text_column
        self.tag_columns = tag_columns

    def __iter__(self):
        for row in self.source.get_dataframe().itertuples():
            text = getattr(row, self.text_column)
            tokens = text.split()
            if self.tag_columns:
                yield TaggedDocument(tokens, [getattr(row, tag_column) for tag_column in self.tag_columns])
            else:
                yield tokens


class FileLineSource(Source):

    def __init__(self, text_file_path, encoding='utf8'):
        self.source_file = text_file_path
        self.encoding = encoding

    def __iter__(self):
        with io.open(self.source_file, mode='rt', encoding=self.encoding) as in_file:
            for line in in_file:
                line = line.strip()
                if len(line) <= 0:
                    continue
                yield line


class OpensubtitlesSentenceSource(Source):

    DEFAULT_SENTENCE_TAG = '<s>'

    def __init__(self, line_source, sentence_tag=None):
        self.source = line_source
        if sentence_tag:
            self.sentence_tag = sentence_tag
        else:
            self.sentence_tag = OpensubtitlesSentenceSource.DEFAULT_SENTENCE_TAG

    def __iter__(self):
        for line in self.source:
            for sentence in line.split(self.sentence_tag):
                yield sentence.strip()


class BZipDocumentSource(Source):

    def __init__(self, bzip_filepath, text_preprocessor=None):
        self.source_filepath = bzip_filepath
        self.text_preprocessor = text_preprocessor
        super().__init__()

    def __iter__(self):
        with bz2.BZ2File(self.source_filepath, 'rtU') as in_bz:
            for line in in_bz:
                text = line
                if self.text_preprocessor:
                    text = self.text_preprocessor.preprocess(text)
                tokens = text.split()
                yield tokens


class GZipDocumentSource(Source):

    def __init__(self, gzip_filepath, text_preprocessor=None):
        self.source_filepath = gzip_filepath
        self.text_preprocessor = text_preprocessor
        super().__init__()

    def __iter__(self):
        with gzip.GzipFile(self.source_filepath, 'rU') as in_bz:
            for line in in_bz:
                text = line
                if self.text_preprocessor:
                    text = self.text_preprocessor.preprocess(text)
                tokens = text.split()
                yield tokens
