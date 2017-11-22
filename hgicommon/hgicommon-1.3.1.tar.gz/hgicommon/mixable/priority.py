"""
Legalese
--------
Copyright (c) 2015 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from abc import ABCMeta


class Priority(metaclass=ABCMeta):
    """
    A model that has a priority, designed for use in `queue.PriorityQueue`.

    Negative numbers have a higher priority than positive ones.
    """
    _NOT_COMPARABLE = "Can only compare to classes implementing 'Priority'"

    MAX_PRIORITY = -sys.maxsize
    MIN_PRIORITY = sys.maxsize

    @staticmethod
    def get_higher_priority_value(value: int):
        """
        Gets a higher priority value than that given.

        Will raise a `ValueError` if already highest priority value.
        :param value: gets a higher priority value than this
        :return: the higher priority value
        """
        if value == Priority.MAX_PRIORITY:
            raise ValueError("Maximum value already")
        return value - 1

    @staticmethod
    def get_lower_priority_value(value: int):
        """
        Gets a lower priority value than that given.

        Will raise a `ValueError` if already lowest priority value.
        :param value: gets a lower priority value than this
        :return: the lower priority value
        """
        if value == Priority.MIN_PRIORITY:
            raise ValueError("Minimum priority already")
        return value + 1

    def __init__(self, priority: int=MIN_PRIORITY):
        self.priority = priority

    def __lt__(self, other):
        if not issubclass(type(other), Priority):
            raise ValueError(Priority._NOT_COMPARABLE)
        return self.priority < other.priority

    def __le__(self, other):
        if not issubclass(type(other), Priority):
            raise ValueError(Priority._NOT_COMPARABLE)
        return self.priority <= other.priority

    def __eq__(self, other):
        if not issubclass(type(other), Priority):
            raise ValueError(Priority._NOT_COMPARABLE)
        return self.priority == other.priority

    def __ge__(self, other):
        if not issubclass(type(other), Priority):
            raise ValueError(Priority._NOT_COMPARABLE)
        return self.priority >= other.priority

    def __gt__(self, other):
        if not issubclass(type(other), Priority):
            raise ValueError(Priority._NOT_COMPARABLE)
        return self.priority > other.priority
