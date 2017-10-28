# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import
import six

from gm.api import PositionSide_Long, PositionSide_Short


# 账户
class Account(object):

    def __init__(self, id, title, cash, positions):
        self.id = id
        self.title = title
        self.cash = cash
        self.inside_positions = positions

    def match(self, title_or_id):
        if self.title == title_or_id:
            return True

        if self.id == title_or_id:
            return True

    def positions(self, symbol='', side=None):
        if not symbol:
            info = list(six.itervalues(self.inside_positions))
            return info

        if not side:
            long_key = '{}.{}'.format(symbol, PositionSide_Long)
            long_info = self.inside_positions.get(long_key)

            short_key = '{}.{}'.format(symbol, PositionSide_Short)
            short_info = self.inside_positions.get(short_key)

            result = []
            if long_info:
                result.append(long_info)
            if short_info:
                result.append(long_info)
            return result

        key = '{}.{}'.format(symbol, side)
        info = self.inside_positions.get(key)
        if not info:
            return []

        return [info]

    def position(self, symbol, side):
        key = '{}.{}'.format(symbol, side)
        return self.inside_positions.get(key)



