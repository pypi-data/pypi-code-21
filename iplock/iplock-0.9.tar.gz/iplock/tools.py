#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2017-02-16 14:51:45
# Filename      : tools.py
# Description   : 

from __future__ import print_function, unicode_literals
import os
import errno

def pid_exists(pid):
    try:
        os.kill(pid, 0)

    except OSError as ex:
        if ex.errno == errno.ESRCH:
            return False

        elif ex.errno == errno.EPERM:
            return True

        else:
            raise

    else:
        return True

