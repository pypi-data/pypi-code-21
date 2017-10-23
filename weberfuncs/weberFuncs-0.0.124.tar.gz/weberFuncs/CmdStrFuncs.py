#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/7/20 16:46"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
专门封装与 CmdStr 相关的功能
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from .WyfPublicFuncs import PrintTimeMsg, IsPython3
from .WyfPublicFuncs import PrintInline, PrintNewline, GetCurrentTime

# WeiYF.20170720 Python2 汉字串测试
"""
Python 2.7.13 (v2.7.13:a06454b1afa1, Dec 17 2016, 20:53:40) [MSC v.1500 64 bit (AMD64)] on win32
>>> s= '汉字ABCD'
>>> type(s)
<type 'str'>
>>> len(s)
10
>>> u = s.encode('utf-8')
Traceback (most recent call last):
  File "<input>", line 1, in <module>
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 0: ordinal not in range(128)
>>> u = s.decode('utf-8')
>>> u
u'\u6c49\u5b57ABCD'
>>> len(u)
6
>>> type(u)
<type 'unicode'>
>>> g = s.decode('GBK')
>>> type(g)
<type 'unicode'>
>>> g
u'\u59f9\u590a\u74e7ABCD'
>>> len(g)
7
>>> u.encode('utf-8')
'\xe6\xb1\x89\xe5\xad\x97ABCD'
>>> s
'\xe6\xb1\x89\xe5\xad\x97ABCD'

"""

# WeiYF.20170720 Python3 汉字串测试
"""
D:\WeberWork\Debug\Tools\apktools\gudouwyf
λ python
Python 3.6.1 (v3.6.1:69c0db5, Mar 21 2017, 18:41:36) [MSC v.1900 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> s = '汉字ABCD'
>>> len(s)
6
>>> type(s)
<class 'str'>
>>> u = s.encode('utf-8')
>>> u
b'\xe6\xb1\x89\xe5\xad\x97ABCD'
>>> type(u)
<class 'bytes'>
>>> len(u)
10
>>> g = s.encode('GBK')
>>> type(g)
<class 'bytes'>
>>> len(g)
8
>>> g
b'\xba\xba\xd7\xd6ABCD'
>>> g.decode('GBK')
'汉字ABCD'
>>> u.decode('utf-8')
'汉字ABCD'
>>> u.decode('GBK')
'姹夊瓧ABCD'
>>> g.decode('utf-8')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xba in position 0: invalid start byte
>>>
"""
# 从上述测试结果可以看出，Python2默认是原生编码，需要转为utf-8；Python3默认就是utf-8编码。
# WeiYF.20170720 CmdStr序列化为串时统一采用utf-8字节编码，单个汉字一般占用3字节。
# Python2: u.encode('utf-8')
# Python3: s.encode('utf-8')


def ToByteArray(s, sEncode='utf8', sSrcEncode=''):
    # 将输入 s 转为 sEncode 编码的字节数组
    # 其中 sEncode=utf8/utf-8/gbk
    # 在Python3中
    r = s
    if not IsPython3():  # Python2
        if type(s) == unicode:
            r = s.encode(sEncode)
        elif type(s) == bytearray:
            r = s.decode(sSrcEncode)
    else:  # Python3
        if type(s) == bytes or type(s) == bytearray:
            # if sSrcEncode and sSrcEncode != sEncode:
            r = s.decode(sSrcEncode)
    return bytearray(r.encode(sEncode))


def PrintHexByteArray(arrayBytes, sHint=''):
    # 打印16进制字节数组
    # arrayData = v
    if type(arrayBytes) != bytearray:
        PrintTimeMsg('PrintHexByteArray.%s.type(arrayBytes) != bytearray' % sHint)
        return
    PrintInline("%s=[\n" % sHint)
    i = 0
    for c in arrayBytes:
        # PrintInline("%.2X " % (ord(c)))
        PrintInline("%.2X " % c)
        i += 1
        if i % 16 == 0: PrintInline("\n")
    PrintInline("\n]\n")


def PrintVariableInfo(v, sHint=''):
    # 打印变量信息
    # PrintTimeMsg('{%s}%s,len(v)=%s=%s=' % (sHint, type(v), len(v), v))
    # PrintTimeMsg('%s{%s.%s}=%s=' % (sHint, type(v).__name__, len(v), v))
    PrintNewline('%s{%s.%s}=%s=' % (sHint, type(v).__name__, len(v), v))


def PrintStringEncodeInfo(v, sHint=''):
    # 打印字符串编码信息
    PrintVariableInfo(v, sHint)
    if type(v) == bytearray:
        PrintHexByteArray(v, sHint)
        return
    if not IsPython3():
        # Python no str.decode()
        PrintVariableInfo(v.decode('utf8'), "  "+ sHint+".decode('utf8')")
    PrintVariableInfo(v.encode('utf8'), "  "+ sHint+".encode('utf8')")


def testPrintVariable():
    s = '汉字ABCD'  # 这种写法的str.len()时单个汉字长度在Python2下时为2，在Python3下为1
    PrintStringEncodeInfo(s, 'str')
    u = u'汉字ABCD'  # 这种写法在Python2/3下都是unicode编码的str类型
    PrintStringEncodeInfo(u, 'utf')
    # PrintStringEncodeInfo(ToByteArray(u), 'u.utf8')
    # PrintStringEncodeInfo(ToByteArray(s), 's.utf8')
    # PrintHexByteArray(bytearray(s.encode('gbk')), 's.gbk1')
    # PrintHexByteArray(ToByteArray(s, 'gbk','utf8'), 's.gbk2')
    ba0 = ToByteArray(u)  # 转为utf8格式字节数组
    PrintHexByteArray(ba0, 'ba0.utf')
    ba1 = ToByteArray(ba0, 'gbk', 'utf8')  # 转为gbk格式字节数组
    PrintHexByteArray(ba1, 'ba1.gbk')
    ba2 = ToByteArray(ba1, 'utf8', 'gbk')  # 转为utf8格式字节数组
    PrintHexByteArray(ba2, 'ba2.utf')

    # g = ToByteArray(u, 'gbk','utf8')
    # PrintHexByteArray(ToByteArray(g, 'utf8', 'gbk'), 's.gbk.3')
    # PrintHexByteArray('ABC123', 'WillError')
    # PrintHexByteArray(ToByteArray('ABC好123', 'utf8'))
    # PrintHexByteArray(ToByteArray('ABC好123', 'gbk'))

# --------------------------------------


def PrintCmdStrArray(CmdStr, sHint=''):
    #  打印CmdStr数组
    CmdCnt = len(CmdStr)
    PrintNewline("[%s]%s.CmdCnt=%d={" % (GetCurrentTime(), sHint, CmdCnt))
    for i in range(CmdCnt):
        PrintVariableInfo(CmdStr[i], '  [%s]' % i)
        # PrintVariableInfo(str(CmdStr[i]), '  ')
        # 在Python2下转为str会改变变量类型，但在Python3下不会。
    PrintNewline("}")


def SerialCmdStrToByteArray(CmdStr):
    # 序列化CmdStr到字节数组
    sRetLen = ''
    baData = bytearray(b'')
    listCmdStr = list(CmdStr)
    for cs in listCmdStr:
        baCmdStr = ToByteArray(cs)
        sRetLen += '%d,' % len(baCmdStr)
        baData += baCmdStr
    if sRetLen: sRetLen = sRetLen[:-1]  # remove tail comma
    sRetLen += ';'  # add semicolon
    return ToByteArray(sRetLen) + baData


def SerialCmdStrFmByteArray(baData):
    # 从字节数组反序列化到CmdStr
    lsCmdStr = []
    if IsPython3():
        iPos = baData.find(ord(';'))
        if iPos<0:
            PrintTimeMsg('SerialCmdStrFmString.iPos=%s,no Semicolon!' % (iPos))
            return lsCmdStr
        lenStr = baData[:iPos].decode('utf8')
        # PrintTimeMsg('lenStr=%s=' % lenStr)
        strData = baData[iPos+1:]
    else:
        sData = baData
        lsPart = sData.partition(';')
        if not lsPart[1]:
            PrintTimeMsg('SerialCmdStrFmString.sData=%s,no Semicolon!' % (sData))
            return lsCmdStr
        lenStr = lsPart[0]
        strData = lsPart[2]
    lsLen = []
    for sLen in lenStr.split(','):
        if sLen:
            try:
                lsLen.append(int(sLen))
            except ValueError:
                PrintTimeMsg('SerialCmdStrFmString.lenStr=%s=Error!' % (lenStr))
                return lsCmdStr
    pB = 0
    for iLen in lsLen:
        sCS = strData[pB:pB+iLen]
        sCS = sCS.decode('utf-8')
        lsCmdStr.append(sCS)
        pB += iLen
    return lsCmdStr


def testSerialCmdStr():
    baT = SerialCmdStrToByteArray([
        'ABCD.TestCmd',
        '汉字ABCD',
        '123456',
        'The quick brown fox jumps over a lazy dog.',
        '这是我的一个秘密，再简单不过的秘密：一个人只有用心去看，才能看到真实。事情的真相只用眼睛是看不见的。——《小王子》',
        '{"ltc": {"XINA50": "0", "totalassets": 299.9034, "marginaccount": "149.9034", "XINA50_orderNum": 1, "netassets": 299.9034, "fltc": "149.9034", "unmatched": 0, "XINA50_frozen": 0, "mainwallet": "150", "fltc_frozen": 0}, "usd": {"marginaccount": 908.79, "BTC2USD_frozen": 913.07, "netassets": 1821.86, "BTC2USD": 908.79, "BTC2USD_orderNum": 5, "totalassets": 1821.86}, "flags": {"XINA50": "0", "GBPUSD": "0", "XAUUSD": "0", "EURUSD": "0", "AUDUSD": "0", "WEEKLYFUTURES": "0", "DAXEUR": "0", "USDJPY": "0", "USDCNH": "0", "XTIUSD": "0", "DAOUSD": "0", "XAGUSD": "0"}, "btc": {"GBPUSD": "1.18", "BTC2USD": "15.21338", "NK225M_orderNum": 0, "XINA50_frozen": 0.2, "XAUUSD_frozen": 0, "AUDUSD_frozen": 0, "XAGUSD_orderNum": 0, "XINA50_orderNum": 0, "DAOUSD_frozen": 0.1, "XAGUSD": "2.93", "unmatched": 1.03, "EURUSD": "1.914", "XTIUSD_frozen": 0.1, "totalassets": 232.72683575, "DAOUSD_orderNum": 0, "GBPUSD_frozen": 0, "XTIUSD_orderNum": 0, "stock_frozen": "0", "XAGUSD_frozen": 0, "marginaccount": "104.89169575", "DAXEUR_orderNum": 0, "XAUUSD": "6.1436", "USDCNH_frozen": 0.1, "BTC2USD_orderNum": 1, "AUDUSD": "12.9503", "NK225M_frozen": 0.1, "DAXEUR": "19.272036", "mainwallet": "126.80514", "fbtc_frozen": 0, "XAUUSD_orderNum": 0, "USDCNH": "1.9316", "EURUSD_orderNum": 0, "USDCNH_orderNum": 0, "EURUSD_frozen": 0, "AUDUSD_orderNum": 0, "XINA50": "16.22941778", "BTC2USD_frozen": 0.33, "netassets": 232.72683575, "NK225M": "3.40699", "fbtc": "0.3", "USDJPY_frozen": 0, "DAXEUR_frozen": 0.1, "USDJPY": "4.9617", "GBPUSD_orderNum": 0, "USDJPY_orderNum": 0, "XTIUSD": "8.0554", "DAOUSD": "10.40327197"}}',
    ])
    PrintHexByteArray(baT, 'baT')
    cs = SerialCmdStrFmByteArray(baT)
    # PrintTimeMsg('cs=%s' % str(cs))
    PrintCmdStrArray(cs,'cs')
# --------------------------------------


def mainCmdStrFuncs():
    # testPrintVariable()
    testSerialCmdStr()


# --------------------------------------
if __name__ == '__main__':
    mainCmdStrFuncs()