# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
This module provides classes for managing tag from source.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import copy

from . import tags_file_reader
from . import tags_logging as logger

LOGGER = logger.get_logger('smart_tags_source', 'info')


class TagsSource:
    """Base TagsSource class."""

    def get_tags(self):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def _filter_tags(self, p_tags, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        l_tags = p_tags
        if not (p_tag_type is None):
            l_tags = [i_tag for i_tag in l_tags if p_tag_type == i_tag['name']]

        if not (p_from is None):
            l_start = p_from
            if p_len is not None:
                l_end = p_from + p_len
                l_tags = [i_tag for i_tag in l_tags if
                          (l_start <= i_tag['start_timestamp'] and i_tag['start_timestamp'] <= l_end)]
            else:
                l_tags = [i_tag for i_tag in l_tags if l_start <= i_tag['start_timestamp']]

        if not (p_func is None):
            l_tags = [i_tag for i_tag in l_tags if p_func(i_tag)]

        return l_tags

    def __deepcopy__(self, memo):
        """Construct a new object, next recursively, inserts copies into it of the :class MemoryTagsSource."""
        return MemoryTagsSource(copy.deepcopy(self.get_tags()))


class MemoryTagsSource(TagsSource):
    """Subclass of class 'TagsSource', stores tags in memory in 'dict' structure."""

    def __init__(self, p_tags=None):
        """
        Initialize tags as dictionary structure.

        :param p_tags: dictionary with tags.
        """
        self._tags = None
        if not (p_tags is None):
            self.set_tags(p_tags)

    def set_tags(self, p_tags):
        """
        Set tags.

        :param p_tag: dictionary with tags.
        """
        self._tags = p_tags

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """
        Get tags of given type.

        :param p_tag_type: type of tag
        :param p_from: start timestamp
        :param p_len: number of tag
        :param p_func: logic  who to choose tag eg. tag['desc'][u'index'] == tag['desc'][u'target']
        :return: filtered tags
        """
        return self._filter_tags(self._tags, p_tag_type, p_from, p_len, p_func)


class FileTagsSource(TagsSource):
    """Subclass of class 'TagsSource', manage tags from file and memory_source."""

    def __init__(self, p_file_path):
        """Initialize tags  proxy, read from p_file if there is no memory_source."""
        self._memory_source = None
        self._tags_proxy = tags_file_reader.TagsFileReader(p_file_path)

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """
        Get tags of given type :param p_tag_type from memory_source or read from p_file.

        :param p_tag_type: type of tag
        :param p_from: start timestamp
        :param p_len: number of tag
        :param p_func: logic  who to choose tag eg. tag['desc'][u'index'] == tag['desc'][u'target']
        """
        if self._memory_source is None:
            return self._filter_tags(
                self._tags_proxy.get_tags(),
                p_tag_type, p_from, p_len, p_func)
        else:
            return self._memory_source.get_tags(p_tag_type, p_from, p_len, p_func)

    def set_tags(self, p_tags):
        """If MemoryTagsSource is not None: set tags in memory_source else: create MemoryTagsSource and set tags."""
        if self._memory_source is None:
            self._memory_source = MemoryTagsSource(p_tags)
        else:
            self._memory_source.set_tags(p_tags)
