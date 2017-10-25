#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore


class StateScriptGenerator:
    stopped = False


class StopScriptGenerator(Exception):
    pass


def customable(func):
    def wrapper(*args, **kwargs):
        scope = sys._getframe().f_back.f_code.co_name
        if scope != '<module>':
            kwargs['now'] = True
        QtCore.QCoreApplication.processEvents()
        if StateScriptGenerator.stopped:
            raise StopScriptGenerator
        return func(*args, **kwargs)
    return wrapper
