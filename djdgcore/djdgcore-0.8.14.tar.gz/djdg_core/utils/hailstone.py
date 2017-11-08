#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/7/30
 """
from __future__ import unicode_literals, absolute_import
import time


class Counter(object):
    """
    自增计数器
    """
    def __init__(self, start=0, size=10000000):
        self.cur_idx = start
        self.size = size

    @property
    def increase(self):
        self.cur_idx += 1
        self.cur_idx %= self.size
        return self.cur_idx

    def increase_timestamp(self, sep='_'):
        return '{0}{1}{2}'.format(
            int(time.time()),
            sep,
            self.increase
        )

simple_counter = Counter()


def regular_url(url):
    """
    规整url   url/path/
    :param url:
    :return:
    """
    if url.startswith('/'):
        url = url[1:]
    if not url.endswith('/'):
        url = '{0}/'.format(url)
    return url
