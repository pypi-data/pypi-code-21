#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/11/7 11:40"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
记录一些运行参数，用于下次运行时加载。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from .WyfPublicFuncs import PrintTimeMsg, ReadTailLines, GetCurrentTime
# from .PrettyPrint import PrettyPrintStr


class CConfigRun:
    def __init__(self, sConfigFN='Config.Run'):
        self.sConfigFN = sConfigFN
        PrintTimeMsg('CConfigRun.sConfigFN=%s=' % self.sConfigFN)

    def SaveInfo(self, sInfo):
        with open(self.sConfigFN, 'a') as f:
            sLine = '%s  # %s\n' % (sInfo, GetCurrentTime())
            f.write(sLine)

    def LoadTail(self, iTailNum=1):
        lsResult = []
        for sLine in ReadTailLines(self.sConfigFN, iTailNum):
            sTm = sLine[-15:]
            sV = sLine[:-19]
            lsResult.append((sV, sTm),)
        return lsResult


def mainCConfigRun():
    o = CConfigRun()
    o.SaveInfo('Test Info')
    sTail = o.LoadTail(2)
    PrintTimeMsg('mainCConfigRun.sTail=%s=' % sTail)


# --------------------------------------
if __name__ == '__main__':
    mainCConfigRun()
