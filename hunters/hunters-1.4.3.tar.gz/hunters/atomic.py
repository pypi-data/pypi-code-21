# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/11
import threading


class AtomicLong(object):
    """ 提供一个原子的递增类 """

    def __init__(self, num=0):
        self.lock = threading.Lock()
        self._value = num

    def incr(self, count=1):
        self.__add__(count)

    def __repr__(self):
        return str(self.value)

    @property
    def value(self):
        return self._value

    def __add__(self, other):
        with self.lock:
            self._value += other
        return self

    def __sub__(self, other):
        with self.lock:
            self._value -= other
        return self
