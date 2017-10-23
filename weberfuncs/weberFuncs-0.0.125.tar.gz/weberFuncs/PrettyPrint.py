#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/7/21 15:26"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
Program description
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""

import sys
from .WyfPublicFuncs import IsPython3, PrintInline
import pprint


class UtfPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if not IsPython3():
            if isinstance(object, unicode):
                sU = object.encode('utf8')
                return "'%s'" % sU, True, False
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


# def Utf8PrettyPrintObj(obj, sHint = ""):
#     PrintInline(sHint)
#     gPP = UtfPrettyPrinter(indent=4)
#     gPP.pprint(obj)
#     sys.stdout.flush()
#
#
# def Utf8PrettyPrintStr(obj):
#     gPP = UtfPrettyPrinter(indent=4)
#     return gPP.pformat(obj)


def PrettyPrintObj(obj, sHint=""):
    PrintInline(sHint)
    gPP = UtfPrettyPrinter(indent=4)
    gPP.pprint(obj)
    sys.stdout.flush()


def PrettyPrintStr(obj):
    gPP = UtfPrettyPrinter(indent=4)
    return gPP.pformat(obj)


def mainPrettyPrint():
    import json
    oJson = {
        'cname': u'姓名',
        'zhangsan': '张三',
        'ename': 'Name',
    }
    PrettyPrintObj(oJson, 'oJson=')
    sJson = '{"cname": "姓名", "zhangsan": "张三", "ename": "Name"}'
    # sJson = json.dumps(oJson)
    objJson = json.loads(sJson)
    PrettyPrintObj(objJson, 'objJson=')
    dictJson = {}
    for key, value in objJson.items():
        dictJson[key] = value
    PrettyPrintObj(dictJson, 'dictJson=')
    print(type(oJson), oJson)
    print(type(dictJson), dictJson)
    # Utf8PrettyPrintObj(oJson, 'oJson')


# --------------------------------------
if __name__ == '__main__':
    mainPrettyPrint()