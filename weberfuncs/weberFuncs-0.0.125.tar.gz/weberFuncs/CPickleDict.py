#! /usr/local/bin/python
#-*- coding:utf-8 -*-

"""
@author: weber.juche@gmail.com
@time: 2016/12/8 9:56

简单封装从文件中存储加载dict的类

"""
import os
import pickle
from .WyfPublicFuncs import PrintTimeMsg, GetFileSizeModTime


class CPickleDict:
    def __init__(self, sFileNameFull):
        self.sFileNameFull = sFileNameFull
        PrintTimeMsg("CPickleDict.sFileNameFull=(%s)" % self.sFileNameFull)

    def Save(self, dictVal):
        with open(self.sFileNameFull, 'wb') as f:
            return pickle.dump(dictVal, f)

    def Load(self):
        if not os.path.exists(self.sFileNameFull):
            return {}
        iSize, sModTm = GetFileSizeModTime(self.sFileNameFull)
        if iSize == 0:
            return {}
        with open(self.sFileNameFull, 'rb') as f:
            return pickle.load(f)


def tryCPickleDict():
    p = CPickleDict('test.pickle')
    print( p.Load())
    print( p.Save({'A': 'a', 'TestHZ': 'english'}))
    print( p.Load())
    print( p.Save({'A': 'a', 'TestHZ': '测试汉字'}))
    print( p.Load())


# -------------------------------
if __name__ == '__main__':
    tryCPickleDict()