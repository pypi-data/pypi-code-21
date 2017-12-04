#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/1 14:08"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装 CNameValueCsv 类，来专门实现 name=value 数据文本存储
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from .WyfPublicFuncs import PrintTimeMsg, GetFileSizeModTime
from .WyfEasyFuncs import DictSortByValue, DictSortByKey
import os


class CNameValueCsv:
    def __init__(self, sFileNameFull):
        self.sFileNameFull = sFileNameFull
        PrintTimeMsg("CNameValueCsv.sFileNameFull=(%s)" % self.sFileNameFull)

    def Save(self, dictNV, bSortByValue=False):
        with open(self.sFileNameFull, 'w') as f:
            if bSortByValue:
                lsKV = DictSortByValue(dictNV)
            else:
                lsKV = DictSortByKey(dictNV)
            for k, v in lsKV:
                sS = "%s=%s\n" % (k, v)
                f.write(sS)

    def Load(self):
        dictNV = dict()
        if not os.path.exists(self.sFileNameFull):
            return dictNV
        iSize, sModTm = GetFileSizeModTime(self.sFileNameFull)
        if iSize == 0:
            return dictNV
        with open(self.sFileNameFull, 'r') as f:
            while True:
                sLine = f.readline()
                if not sLine: break
                sLine = sLine.strip()
                sN, cSep, sV = sLine.partition('=')
                if cSep:
                    dictNV[sN] = sV
        return dictNV


def mainCNameValueCsv():
    p = CNameValueCsv('test.txt')
    PrintTimeMsg(p.Load())
    PrintTimeMsg(p.Save({'A': 'a', 'TestHZ': 'english'}))
    PrintTimeMsg(p.Load())
    PrintTimeMsg(p.Save({'A': 'a', 'TestHZ': '测试汉字', '0':'zero'}))
    PrintTimeMsg(p.Load())


# --------------------------------------
if __name__ == '__main__':
    mainCNameValueCsv()
