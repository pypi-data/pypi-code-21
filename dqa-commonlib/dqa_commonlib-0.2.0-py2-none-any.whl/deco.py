# -*- coding:utf-8 -*-
# Author: lijian01
# Mail: lijian01@imdada.cn

import functools
import subprocess


def record(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print "before called [%s]." % func.__name__
        fn = func(*args, **kwargs)
        print "after called [%s]." % func.__name__
        return fn

    return wrapper
