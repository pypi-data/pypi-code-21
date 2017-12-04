#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/4 11:17"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装一些技巧函数。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from .WyfPublicFuncs import PrintTimeMsg
import operator


def DictSortByValue(dictVal):
    # 字典按取值排序，返回 [(key,value)] 元组列表
    return sorted(dictVal.items(), key=operator.itemgetter(1))


def DictSortByKey(dictVal):
    # 字典按键排序，返回 [(key,value)] 元组列表
    return sorted(dictVal.items(), key=operator.itemgetter(0))


def mainWyfEasyFuncs():
    dictV = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0, 12: 100}
    oRet = DictSortByValue(dictV)
    PrintTimeMsg('DictSortByValue(%s)=%s=' % (dictV, oRet))
    oRet = DictSortByKey(dictV)
    PrintTimeMsg('DictSortByKey(%s)=%s=' % (dictV, oRet))


# --------------------------------------
if __name__ == '__main__':
    mainWyfEasyFuncs()
