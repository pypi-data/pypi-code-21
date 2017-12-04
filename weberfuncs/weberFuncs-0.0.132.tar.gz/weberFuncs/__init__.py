#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""    
    2015/10/14  WeiYanfeng
    公共函数 包

~~~~~~~~~~~~~~~~~~~~~~~~
共函数 包
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install redis

"""
# WeiYF.20170605 经测试，Python3引用当前目录下的源码文件，文件名前要加`.`点号
# 同时这样的写法也可以在Python2.7下使用。

from .WyfPublicFuncs import GetCurrentTime, GetUnixTimeStr, GetUnixTimeLocal, \
    GetLocalTime, GetYYYYMMDDhhnnss, GetCurrentTimeMS, GetCurrentTimeMSs, \
    GetTimeInteger, GetTimeIntMS, GetTimeStampIntFmYMDHns, IsPython3

from .WyfPublicFuncs import YMDhnsAddSeconds, YMDhnsXxxAddMSecs
from .WyfPublicFuncs import AddSubMonthYYYYMM, AddSubDayYYYYMMDD
from .WyfPublicFuncs import ReturnWeekDayFmYMD, ReturnWeekNumFmYMD

from .WyfPublicFuncs import PrintInline, PrintNewline, PrintTimeMsg, PrintfTimeMsg, \
    PrintMsTimeMsg, PrintAndSleep, LoopPrintSleep, printCmdString, printHexString

from .WyfPublicFuncs import GetRandomInteger, ConvertStringToInt32, GetCodeFmString, \
    crc32, md5, sha1, md5file

from .WyfPublicFuncs import GetSrcParentPath, GetCriticalMsgLog, CAppendLogBase, \
    WyfAppendToFile
from .CLogTagMsg import CLogTagMsg
from .WyfPublicFuncs import JoinGetFileNameFmSrcFile
from .WyfHttpFuncs import RequestsHttpGet, RequestsHttpPost, RequestsHttpPostForm, \
    RequestsDownLoad, RequestsHttpPostFormData
from .WyfPublicFuncs import CatchExcepExitTuple, CatchExcepExitParam

from .WyfPublicFuncs import ClassForAttachAttr
from .WyfPublicFuncs import GetSystemPlatform
from .WyfPublicFuncs import ReadTailLines, ReadLargeFileDo, GetFileSizeModTime
from .CConfigRun import CConfigRun

from .WyfCryptoFuncs import ToHexString, FmHexString, AesCbcHexEncryt, AesCbcHexDecryt

from .WyfEasyFuncs import DictSortByValue, DictSortByKey
from .ExecCmdFuns import ExecCmdWaitByPopen, ExecCmdWaitOutErrByPopen

from .CmdStrFuncs import ToByteArray, PrintHexByteArray, PrintCmdStrArray, \
    SerialCmdStrToByteArray, SerialCmdStrFmByteArray

from .PrettyPrint import PrettyPrintObj, PrettyPrintStr

from .CRunCronTask import CRunCronTask

from .CPickleDict import CPickleDict
from .CNameValueCsv import CNameValueCsv

from .CSendSMTPMail import CSendSMTPMail
from .CSendCustomMsgWX import CSendCustomMsgWX

from .CSerialJson import CSerialJson
from .CHttpJsonClient import CHttpJsonClient

from .SimpleShiftEncDec import SimpleShiftEncode, SimpleShiftDecode

from .WyfSupplyFuncs import get_total_size
from .WyfQueueThread import StartThreadDoSomething, CThreadCacheByQueue, CThreadDiscardDeal

# from .JsonRpcFuncs import # WeiYF.20161206 该单元暂保留，不输出
# WeiYF.20170605 将 redis 相关封装转移到 weberRedis 包
# from .CRedisSubscribe import GetRedisClient,CRedisSubscribe,RedisPipeWatchExec
# from .CAutoConnectRedis import CAutoConnectRedis

from .CHandleCmd_BaseService import RegisterForHandleCmdService, CHandleCmd_BaseService

