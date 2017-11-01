#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2017-02-16 14:27:57
# Filename      : __init__.py
# Description   : 

from __future__ import print_function, unicode_literals
from .lock import IPLocker
import tempfile
import os.path

__ALL__ = ["locked", "IP", "lock", "unlock"]

LK_PATH = os.path.join(tempfile.gettempdir(), "iplock/")

_locker = IPLocker(LK_PATH)
lock = _locker.lock
unlock = _locker.unlock

IP = _locker.get

class lock_with(object):
    def __init__(self, ip, *args, **kwargs):
        self.ip = ip
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        lock(self.ip, *self.args, **self.kwargs)

    def __exit__(self, e_t, e_v, t_b):
        unlock(self.ip)
        return False

