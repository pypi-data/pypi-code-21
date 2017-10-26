#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:26
# @Author  : Hou Rong
# @Site    : 
# @File    : Common.py
# @Software: PyCharm
from __future__ import unicode_literals

import six
from functools import partial, reduce
from operator import getitem
from collections import defaultdict

MIN_PRIORITY = 1


def is_legal(s):
    if s:
        if isinstance(s, six.string_types):
            if s.strip():
                if s.lower() != 'null':
                    return True
        elif isinstance(s, six.integer_types):
            if s > -1:
                return True

        elif isinstance(s, float):
            if s > -1.0:
                return True
    return False


def is_chinese(uchar):
    """
    判断一个 unicode 是否是汉字
    :type uchar: unicode
    :return: bool
    """
    if "\u4e00" <= uchar <= "\u9fa5":
        return True
    else:
        return False


def is_number(uchar):
    """
    判断一个 unicode 是否是数字
    :type uchar: unicode
    :return: bool
    """
    if '\u0030' <= uchar <= '\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """
    判断一个 unicode 是否是英文字母
    :type uchar: unicode
    :return: bool
    """
    if ('\u0041' <= uchar <= '\u005a') or ('\u0061' <= uchar <= '\u007a'):
        return True
    else:
        return False


def is_latin(uchar):
    """
    判断一个 unicode 是否是拉丁字母以及拉丁衍生字母
    :type uchar: unicode
    :return: bool
    """
    if ('\u0041' <= uchar <= '\u005a') or ('\u0061' <= uchar <= '\u007a') or ('\u00c0' <= uchar <= '\u00d6') or (
                    '\u00d8' <= uchar <= '\u00f6') or ('\u00f8' <= uchar <= '\u00ff'):
        return True
    else:
        return False


def is_latin_and_punctuation(uchar):
    """
        判断一个 unicode 是否是拉丁字母以及拉丁衍生字母以及相应富豪
        :type uchar: unicode
        :return: bool
        """
    if ('\u0020' <= uchar <= '\u007e') or ('\u00a0' <= uchar <= '\u00ff'):
        return True
    else:
        return False


def is_all(string, check_func=is_chinese):
    return all(check_func(c) for c in string)


def has_any(string, check_func=is_chinese):
    return any(check_func(c) for c in string)


def key_modify(s):
    return s.strip().lower()


def get_or_default(a, b, default):
    """
    get b from a if exists else return default
    :param a:
    :param b:
    :param default:
    :return:
    """
    if isinstance(a, list):
        a = a[0]
    if hasattr(a, '__contains__'):
        if b in a:
            return getitem(a, b)
        else:
            return default
    else:
        return default


def dot_get(target_dict, *args, **kwargs):
    default = kwargs.get('default', '')
    if len(args) == 0:
        return default
    for arg in args:
        res = reduce(partial(get_or_default, default=default), arg.split('.'), target_dict)
        if res != default:
            return res
    return default


def i_do_not_care_list_or_dict(s):
    if isinstance(s, dict):
        yield s
    elif isinstance(s, list):
        for i in s:
            yield i
    elif isinstance(s, six.string_types):
        pass
    else:
        raise Exception("Unknown Type {0}".format(type(s)))


class GetKey(object):
    def __init__(self):
        self.priority = defaultdict(list)
        self.filter = is_legal

    def update_priority(self, priority):
        """
        update key's priority
        priority will like this

        {
            ['name', 'name_en']: {
                'source_1': 10,
                'source_2': 9
                ,
                'source_3': 8
            },
            ['grade', 'star']: {
                'source_1': 8,
                'source_2': 10,
                'source_3': 6
            },
            'default': None
        }

        1 level is key's name
        2 level is source name
        3 level is priority

        :type priority: dict
        :return: value your want
        """
        self.priority.update(priority)

    def update_filter(self, legal_filter):
        """
        filter is a function which can check your value is legal,
        if the value is not legal, we will use the lower priority
        key's value
        :param legal_filter:
        :return:
        """
        self.filter = legal_filter

    def get_key_by_priority_or_default(self, src, key_name='default', default='', special_filter=None):
        """
        get value from dict by key's priority or default value
        :type src: dict
        :type key_name: str
        :type default: str
        :return: default or highest priority and legal key's value
        """
        if len(src.keys()) == 0:
            return default

        # get priority dict or default
        priority = None
        for k, v in self.priority.items():
            if key_name in k:
                priority = v
        if not priority:
            priority = self.priority['default']

        # get values
        for k, v in sorted(
                src.items(),
                key=lambda x: priority.get(x[0], priority.get('default', MIN_PRIORITY)),
                reverse=True):
            if special_filter:
                if special_filter(v):
                    return v
            else:
                if self.filter(v):
                    return v
        return default
