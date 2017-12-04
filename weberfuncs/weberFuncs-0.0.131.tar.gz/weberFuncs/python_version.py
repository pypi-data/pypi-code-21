#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/6/5 15:13"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
提供判断Python解释器版本的函数
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""

import sys


def GetPythonVersionMajor():
    """
    得到 python 主要版本号
    >>> import sys
    >>> sys.version_info
    sys.version_info(major=3, minor=6, micro=1, releaselevel='final', serial=0)
    >>> sys.version_info.major
    3
    """
    return sys.version_info.major


def IsPython2OrBefore():
    # 判断是否是 Python 2 及之后版本
    return GetPythonVersionMajor() < 3


def IsPython3OrLater():
    # 判断是否是 Python 3 及之后版本
    return GetPythonVersionMajor() >= 3

# --------------------------------------
if __name__ == '__main__':
    print(sys.version)
    print(sys.version_info)
    print('IsPython2OrBefore()=' + str(IsPython2OrBefore()))
    print('IsPython3OrLater()=' + str(IsPython3OrLater()))