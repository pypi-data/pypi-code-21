# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

import functools


def db_log(action):
    """记录日志到数据库"""
    def _db_log(fn):
        @functools.wraps(fn)
        def __db_log(*args, **kwargs):
            result = fn(*args, **kwargs)
            print(action)
            # self.addLog(request, self.get_change_message(), LogActionEnum.DELETE, **kwargs)
            return result
        return __db_log
    return _db_log
