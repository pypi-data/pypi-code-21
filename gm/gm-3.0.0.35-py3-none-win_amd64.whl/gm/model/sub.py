# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

from gm.constant import SUB_ID, SUB_TAG
from gm.model.storage import context


class SubDetail(object):
    def __init__(self, symbol, frequency, count, wait_group, wait_group_timeout, unsubscribe_previous):
        self.symbol = symbol
        self.frequency = frequency
        self.count = count
        self.wait_group = wait_group
        self.wait_group_timeout = wait_group_timeout
        self.unsubscribe_previous = unsubscribe_previous

    @property
    def id(self):
        # 唯一标识
        return SUB_ID.format(self.symbol, self.frequency, self.count)

    @property
    def unique(self):
        # 看看是否订阅过
        return self.id not in [sub.id for sub in context.inside_bar_subs]

    def __repr__(self):
        return self.id

    @property
    def sub_tag(self):
        # 取消订阅标签& 查找订阅最大值时用
        return SUB_TAG.format(self.symbol, self.frequency)
