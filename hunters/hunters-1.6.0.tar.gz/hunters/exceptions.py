# -*- coding:utf-8 -*-
# Created by qinwei on 2017/9/11
import logging

logger = logging.getLogger("hunters.exception")


class OverLimitErr(Exception):
    """ Add Url Over limit """


class SpiderExceptionListener(object):
    """
    总的Exception控制器
    """

    def __init__(self):
        self._exception_handler = []
        self.init_exception()

    def init_exception(self):
        def show_exception(ex):
            logger.exception(ex)

        self.add_listener(show_exception)

    def add_listener(self, ex):
        if not callable(ex):
            raise ValueError("{} not callable")
        self._exception_handler.append(ex)

    def handle_exception(self, ex):
        for handler in self._exception_handler:
            handler(ex)


spider_exception_listener = SpiderExceptionListener()
