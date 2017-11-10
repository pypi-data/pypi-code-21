# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/31
import logging
import tracemalloc
from time import time, sleep

LOGGER = logging.getLogger("hunters.benchmark")

class BenchMark(object):
    """
    一个耗时记录器
    here = BenchMark()

    here.mark()
    your code ...
    here.mark("ccc") : show ... ccc times 0.003 ms
    your code..
    here.mark("xxxx")  show ... xxxx times 0004 ms from mark.here('ccc') default
    here.mark('total', 'cccc')  show ... total  time 0.007 from mark(ccc)
    """
    DEFAULT_MARK_NAME = "init"

    def __init__(self, start_mark=None, logger=None):
        self.last_key = start_mark or self.DEFAULT_MARK_NAME
        self.all_mark = {self.last_key: time()}
        self.logger = LOGGER or logger

    def mark(self, name=None, from_mark=None, extra_msg=""):
        last_mark_key = self.last_key
        if name and from_mark:
            assert from_mark in self.all_mark, "Can't find mark[%s]" % from_mark
            last_mark_key = from_mark

        if name:
            self.logger.debug("[%s]->[%s]\t[%.3f]s %s" % (last_mark_key, name, time() - self.all_mark.get(last_mark_key), extra_msg))
            self.all_mark[name] = time()
        else:
            name = self.DEFAULT_MARK_NAME
        self.last_key = name


def timeit(fn):
    """用一个装饰器包裹方法, 计算耗时"""

    def decorator(*args, **kwargs):
        b = BenchMark(fn.__name__)
        result = fn(*args, **kwargs)
        b.mark(fn.__name__ + " OK")
        return result

    return decorator


if __name__ == "__main__":
    ch = logging.StreamHandler()
    FORMAT = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(module)s[%(lineno)d]-%(message)s")
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(FORMAT)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(ch)

    here = BenchMark()

    here.mark("st")
    sleep(0.01)
    here.mark("name")
    sleep(0.02)
    here.mark("two")
    here.mark("total", "name")
