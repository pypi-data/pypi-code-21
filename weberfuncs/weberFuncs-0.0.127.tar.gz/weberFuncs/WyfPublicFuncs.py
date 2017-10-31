#!/usr/local/bin/python
#-*- coding:utf-8 -*-

"""
    2015/10/15  WeiYanfeng
    常用公共函数，都是需要导出的
"""

import time
import sys


def IsPython3():
    # 判断是否是 Python 3
    return sys.version > '3'

if not IsPython3():
    reload(sys)
    sys.setdefaultencoding('utf-8') #WeiYF.20150114 强制转为 utf-8 编码


def GetCurrentTime():
    return time.strftime("%Y%m%d-%H%M%S")


def GetUnixTimeStr(tmInt):
    return time.strftime("%Y%m%d-%H%M%S",time.gmtime(tmInt))


def GetUnixTimeLocal(tmInt):
    return time.strftime("%Y%m%d-%H%M%S",time.localtime(tmInt))


def GetLocalTime(iSeconds):
    return time.localtime(time.time()+iSeconds)


def GetYYYYMMDDhhnnss(iSeconds):
    return time.strftime("%Y%m%d-%H%M%S",time.localtime(time.time()+iSeconds))


def PrintInline(sMsg):
    try:
        sys.stdout.write(sMsg)
        sys.stdout.flush()
    except UnicodeError as e:
        printHexString('UnicodeDecodeError=', sMsg)


def PrintNewline(sMsg):
    PrintInline('%s\n' % sMsg)


def PrintTimeMsg(sMsg):
    PrintInline("[%s]%s\n" % (GetCurrentTime(), sMsg))


def PrintfTimeMsg(fmt, *args, **kwargs):
    if IsValueString(fmt):
        sArg = fmt % args
    else:
        sArg = '%s:%s' % (str(fmt),str(args))
    sKw = str(kwargs) if kwargs else ''
    PrintTimeMsg(sArg+sKw)


def GetCurrentTimeMS(iTimeDiff=0):
    # return  '2015-05-19 18:22:55.681'
    # import datetime
    # # sTimeString = datetime.datetime.now() #2015-05-21 17:32:13.750000
    # sTimeString = str(datetime.datetime.fromtimestamp(time.time()+iTimeDiff))
    # # print "sTimeString=",sTimeString
    # return sTimeString[:-3] # 保留到毫秒级
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def GetCurrentTimeMSs(iTimeDiff=0):
    # return  '2015-05-19 18:22:55.681'
    # import datetime
    # # sTimeString = datetime.datetime.now() #2015-05-21 17:32:13.750000
    # sTimeString = str(datetime.datetime.fromtimestamp(time.time()+iTimeDiff))
    # # print "sTimeString=",sTimeString
    # return sTimeString[:-3] #保留到毫秒级
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')[:-3]


def PrintMsTimeMsg(sMsg):
    import datetime
    PrintInline("[%s]%s\n" % (str(datetime.datetime.now())[:-3],sMsg))

# ------------------------------


def PrintAndSleep(sleepSeconds, sHint, bVerbose=True):
    if bVerbose:
        PrintTimeMsg("%s.sleep(%ss)..." % (sHint,sleepSeconds))
    time.sleep(sleepSeconds)


def LoopPrintSleep(sleepSeconds, iPrintCount, sHint):
    iLoopCnt = 0
    while True:
        PrintAndSleep(sleepSeconds,'%s.iLoopCnt=%s' % (sHint,iLoopCnt),
                      iLoopCnt%iPrintCount==0)
        iLoopCnt += 1
# ------------------------------


def GetTimeInteger():
    return int(time.time())


def GetTimeIntMS():
    return int(time.time()*1000)


def GetTimeStampIntFmYMDHns(s):
    # 返回时间戳整数
    # dateFormat = "%Y%m%d-%H%M%S"
    # dt = time.strptime(sYmdHns, dateFormat)
    # return int(time.mktime(dt))
    ts = time.mktime((int(s[0:4]), int(s[4:6]), int(s[6:8]),
                      int(s[9:11]), int(s[11:13]), int(s[13:15]), -1,-1,-1))
    return int(ts)


def YMDhnsAddSeconds(sYMDhns, iSeconds):
    """
        为 sYMDhns 格式的时间加减秒数
        :param sYMDhns: 基础时间 (YYYYMMDD-hhnnss)
        :param iSeconds: 要增加的秒数，负值表示减少
        :return: 返回计算后的时间 (YYYYMMDD-hhnnss)
    """
    iTm = GetTimeStampIntFmYMDHns(sYMDhns)
    iTm += iSeconds
    return GetUnixTimeLocal(iTm)


def YMDhnsXxxAddMSecs(sYmdHnsXxx, iMSecs):
    """
        为 sYMDhnsXxx 格式的时间加减毫秒数
        :param sYmdHnsXxx: 基础时间 (YYYYMMDD-hhnnss.xxx)
        :param iMSecs: 要增加的毫秒数，应取正值
        :return: 返回计算后的时间 (YYYYMMDD-hhnnss.xxx)
    """
    if len(sYmdHnsXxx) != 19:
        return 'YYYYMMDD-hhnnss.xxx'
    iXxx = int(sYmdHnsXxx[-3:])
    iSec, iMSec = divmod(iMSecs+iXxx, 1000)
    # PrintTimeMsg('YMDhnsXxxAddMSecs(%s,%s)' % (iSec, iMSec))
    sYmdHns = YMDhnsAddSeconds(sYmdHnsXxx[0:15], iSec)
    sResult = '%s.%.3d' % (sYmdHns, iMSec)
    # PrintTimeMsg('YMDhnsXxxAddMSecs(%s,%s).sResult=%s=' % (sYmdHnsXxx, iMSecs, sResult))
    return sResult


def AddSubDayYYYYMMDD(sYYYYMMDD, iDayNum):
    """
        为 YYYYMMDD 格式的日期加减天数
        :param sYYYYMMDD: 基础年月
        :param iDayNum: 要增加的月份数，负值表示递减
        :return: 返回计算后的日期
    """
    import datetime
    # PrintTimeMsg('AddSubDayYYYYMMDD.sYYYYMMDD=%s=' % (sYYYYMMDD))
    if iDayNum == 0: return sYYYYMMDD
    if sYYYYMMDD == 'YYYYMMDD': return sYYYYMMDD # WeiYF.20160106 避免异常
    if sYYYYMMDD is None: return 'YYYYMMDD' # WeiYF.20160106 避免异常
    dateFormat = "%Y%m%d"
    dt = datetime.datetime.strptime(sYYYYMMDD, dateFormat)
    dtRet = dt + datetime.timedelta(days=iDayNum)
    return dtRet.strftime(dateFormat)


def AddSubMonthYYYYMM(sYYYYMM, iMonthNum):
    """
        为 YYYYMM 格式的年月加减月份
        :param sYYYYMM: 基础年月
        :param iMonthNum: 要增加的月份数，负值表示递减
        :return: 返回计算后的年月
    """
    iYYYY = int(sYYYYMM[0:4])
    iMM = int(sYYYYMM[4:6])
    iV = (iMM-1)+iYYYY*12
    iV += iMonthNum
    iY = iV / 12
    iM = iV % 12+1
    sRetYYYYMM = "%.4d%.2d" % (iY,iM)
    # PrintTimeMsg('AddSubMonthYYYYMM(%s,%s)=%s=' % (sYYYYMM, iMonthNum, sRetYYYYMM))
    return sRetYYYYMM


def ReturnStructFmYMD(sYMD):
    # 从 sYMD 得到星期几 0=星期日~6＝星期六
    return time.strptime(sYMD, '%Y%m%d')


def ReturnWeekDayFmYMD(sYMD):
    # 从 sYMD 得到星期几 0=星期日~6＝星期六
    tmStruct = ReturnStructFmYMD(sYMD)
    return (tmStruct.tm_wday+1) % 7


def ReturnWeekNumFmYMD(sYMD):
    # 从 sYMD 得到当年第几周
    tmStruct = time.strptime(sYMD,'%Y%m%d')
    return time.strftime('%U',tmStruct) # 以星期天为周的第一天
    # return  time.strftime('%W',tmStruct) # 以星期一为周的第一天

# ------------------------------


def printCmdString(sHint,CmdStr):  # 采用列表来存储CmdStr入口参数
    CmdCnt = len(CmdStr)
    PrintNewline("[%s]%s.CmdCnt=%d={" % (GetCurrentTimeMS(),sHint,CmdCnt))
    for i in range(CmdCnt):
        try:
            if IsValueString(CmdStr[i]):
                sUTF = CmdStr[i]
                if IsPython3():
                    pass
                else:
                    if not IsUtf8String(sUTF):
                        sUTF = sUTF.decode('GBK').encode('utf-8')
            else:
                sUTF = str(CmdStr[i])
        except UnicodeDecodeError as e:
            # sUTF = CmdStr[i]
            pass
        # PrintNewline("  CmdStr[%d].%d=%s=" % (i,len(CmdStr[i]),sUTF))
        PrintNewline("  CmdStr[%d].%d=%s=" % (i, len(sUTF), sUTF))
    PrintNewline("}")


def printHexString(sHint, arrayData):
    if arrayData is None: return
    PrintInline("%s=[\n" % sHint)
    i = 0
    for c in arrayData:
        PrintInline("%.2X " % (ord(c)))
        i += 1
        if i % 16 == 0: PrintInline("\n")
    PrintInline("\n]\n")

# ------------------------------


def IsUtf8String(sStr):
    # 判断一个串是否是 UTF-8 编码
    valid_utf8 = True
    if IsPython3():
        pass
    else:
        try:
            sStr.decode('utf-8')
        except UnicodeDecodeError as e:
            valid_utf8 = False
    return valid_utf8


def IsValueString(oVal):
    # 判断一个变量是否是 串
    if isinstance(oVal, str):
        return True
    if IsPython3():
        return False
    else:
        if isinstance(oVal, unicode):
            return True
        else:
            return False

# ------------------------------


def GetRandomInteger(iNum=8):
    # 生成十进制有 iNum 位的随机数
    import random
    return random.randint(pow(10,iNum-1), pow(10,iNum)-1) # sys.maxint/2


def ConvertStringToInt32(sString):
    sMD5 = md5(sString)
    sHex = sMD5[-8:]  # 4 bytes
    iInt = int(sHex, 16)
    return iInt

# ------------------------------


def JoinGetFileNameFmSrcFile(srcfile, lsFN, iDiscard=0):
    """
    根据源文件得到其所在目录，然后拼接生成目标文件名。
    :param srcfile: 源文件名，调用时一般填 __file__
    :param lsFN: 要追加的目录和文件名列表
    :param iDiscard: 得到源文件名所在路径后，需要丢弃的目录层级
    :return: 拼接好的目标文件名，会自动区分Unix/Windows路径分隔符
    """
    import os.path
    cSep = os.path.sep
    sDir = os.path.dirname(os.path.realpath(srcfile))
    lsDir = sDir.split(cSep)
    if iDiscard>0:
        lsDir = lsDir[:-iDiscard]
    lsDir.extend(lsFN)
    return cSep.join(lsDir)


def GetSrcParentPath(srcfile, bUp=True):
    """
        取指定代码文件上级目录的绝对路径
        bUp=True 取上级目录
        bUp=False 取当前目录
    """
    # import os
    import os.path
    if srcfile:
        sDir = os.path.dirname(os.path.realpath(srcfile))
        lsDir = sDir.split(os.sep)
        if bUp:
            sDir = os.sep.join(lsDir[:-1])
        else:
            sDir = os.sep.join(lsDir[:])
        return sDir+os.sep
    else:
        PrintTimeMsg("Please use GetSrcParentPath(__file__)! Exit!")
        sys.exit(-1)


class GetCriticalMsgLog():
    # 生成输出关键信息的对象
    def __init__(self, sPathParam='@.', bUp=True):
        # 初始路径支持如下情况:
        #   1.依据代码文件 调用时传入 __file__ 计算出上一级路径
        #   2.使用当前工作路径；无需传入； 相当于 __file__ 取值为 . #os.getcwd()
        #   3.指定特定路径； 直接传入指定目录
        # 如果 sPathParam 中存在 @ 则表示是 __file__ 情况，@前面是路径转换后的子目录
        # 调用时传入 'log@'+__file__ 即可得到当前源码的上级目录
        iPos = sPathParam.find('@')
        if iPos<0:
            self.sLogPath = sPathParam
        else:
            self.sLogPath = GetSrcParentPath(sPathParam[iPos+1:], bUp)+sPathParam[0:iPos]
        PrintTimeMsg('GetCriticalMsgLog.sLogPath=%s=' % self.sLogPath)

    def log(self, sTagFN, sMsg, sExt="log"):
        import os
        sFNameOut = self.sLogPath+os.sep+"wyf"+sTagFN+"."+sExt
        with open(sFNameOut, "a") as f:  # 追加模式输出
            sS = "[%s]%s\n" % (GetCurrentTimeMSs(),sMsg)
            f.write(sS)

    def logFile(self, sMsg):
        # WeiYF.20151106 直接输出到指定文件
        sFNameOut = self.sLogPath
        with open(sFNameOut,"a") as f: # 追加模式输出
            sS = "[%s]%s\n" % (GetCurrentTimeMSs(),sMsg)
            f.write(sS)

    def chkRename(self, sTagFN, iSizeMB, sBakTag='bak'):
        # 将 sFileDir 目录下，大于 iSizeMB 的文件，重新命名为原文件名+当前日期形式。
        import os
        sDir = self.sLogPath+os.sep
        sFN = "wyf"+sTagFN+".log"
        sSrcDirFN = sDir+sFN
        iSizeInt = (1024*1024)*iSizeMB
        if os.path.getsize(sSrcDirFN)>iSizeInt:
            sBase, sExt = os.path.splitext(sFN)
            sOutFN = '%s_%s%s' % (sBase, GetCurrentTime(), sExt) # [0:8]
            try:
                # WeiYF.20160421 采用renames会自动创建子目录
                sOutDir = self.sLogPath+os.sep+sBakTag+os.sep
                os.renames(sSrcDirFN,sOutDir+sOutFN)
                PrintTimeMsg('rename(%s->%s)OK!' % (sSrcDirFN, sOutFN))
            except WindowsError:
                import traceback
                PrintTimeMsg(traceback.format_exc())


class CAppendLogBase:
    """
        WeiYF.20160512 新增基类，附带 WyfAppendToFile 成员函数
        主要借助 __file__ 获取到当前目录，并在上级目录下的log子目录下写入日志
        应用示例如下：
        gLog = CAppendLogBase(__file__)
        def LogTagError(sTagFN, sMsg):
            global gLog
            gLog.WyfAppendToFile(sTagFN,sMsg)
    """
    def __init__(self, sLogFileName, sLogSubDir='log', bUp=True):
        self.cmLog = GetCriticalMsgLog(sLogSubDir+'@'+sLogFileName, bUp)

    def WyfAppendToFile(self, sTagFN, sMsg, sExt="log"):
        self.cmLog.log(sTagFN, sMsg, sExt)


def WyfAppendToFile(sFullPathFNameOut,sMsg):
    # 直接追加方式输出到文件
    with open(sFullPathFNameOut,"a") as f: # 追加模式输出
        sS = "[%s]%s\n" % (GetCurrentTime(),sMsg)
        f.write(sS)


class ClassForAttachAttr(object):
    """
        WeiYF.20151029 为了更好设置保存动态属性，引入的类
    """
    def __init__(self):
        pass

    def __str__(self):
        return 'ClassForAttachAttr=%s=' % ( str(self.__dict__))


def GetSystemPlatform():
    # 返回当前操作系统类型
    import platform
    return platform.system()

# --------------------------------------
# WeiYF.20161202 取消该函数
# def Include(filename):
#     """
#         用于包含一些公共单元
#     """
#     if os.path.exists(filename):
#         execfile(filename)


def CatchExcepExitTuple(bThread, sHint, callbackFunc, tupleCallbackParam):
    # 采用元组方式传入参数，调用回调函数，出现异常则退出程序
    try:
        return callbackFunc(*tupleCallbackParam)
    except Exception as e:
        import sys, traceback, os
        traceback.print_exc() # WeiYF.20151022 打印异常整个堆栈 这个对于动态加载非常有用
        PrintTimeMsg('%s.Exception={%s}EXIT!' % (sHint, str(e)))
        if bThread: os._exit(-1)
        else: sys.exit(-1)


def CatchExcepExitParam(bThread, sHint, callbackFunc, *args, **kwargs):
    # 顺序传入原有参数，调用回调函数，出现异常则退出程序
    try:
        return callbackFunc(*args, **kwargs)
    except Exception as e:
        import sys,traceback,os
        traceback.print_exc() # WeiYF.20151022 打印异常整个堆栈 这个对于动态加载非常有用
        PrintTimeMsg('%s.Exception={%s}EXIT!' % (sHint,str(e)))
        if bThread: os._exit(-1)
        else: sys.exit(-1)

# -------------------------------------------------------


def GetCodeFmString(sStr, cSep=' '):
    # 从 "Code Value" 格式串中拆分出 Code 和 Value
    cv = sStr.split(cSep, 1)
    if len(cv) >= 2:
        return tuple(cv)
    return sStr,''


def crc32(sS):
    import binascii
    return '%.8X' % (binascii.crc32(sS) & 0xffffffff)

# --------------------------------------


def md5(sS):
    import hashlib
    m = hashlib.md5()
    if IsPython3():
        m.update(sS.encode('utf-8'))
    else:
        m.update(sS)
    return m.hexdigest()


def sha1(sS):
    import hashlib
    m = hashlib.sha1()
    if IsPython3():
        m.update(sS.encode('utf-8'))
    else:
        m.update(sS)
    return m.hexdigest()


def md5file(fname):
    import hashlib
    oHash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            oHash.update(chunk)
    return oHash.hexdigest()

# -------------------------------


def ReadTailLines(sFileName, total_lines_wanted):
    """
        从 sFileName 中读取尾部 total_lines_wanted 条记录
        参考 http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    BLOCK_SIZE = 1024
    with open(sFileName, 'rb') as f:
        f.seek(0, 2)
        block_end_byte = f.tell()
        lines_to_go = total_lines_wanted
        block_number = -1
        blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                    # from the end of the file
        while lines_to_go > 0 and block_end_byte > 0:
            if block_end_byte - BLOCK_SIZE > 0:
                # read the last block we haven't yet read
                f.seek(block_number*BLOCK_SIZE, 2)
                blocks.append(f.read(BLOCK_SIZE))
            else:
                # file too small, start from begining
                f.seek(0,0)
                # only read what was not read
                blocks.append(f.read(block_end_byte))
            lines_found = blocks[-1].count('\n')
            lines_to_go -= lines_found
            block_end_byte -= BLOCK_SIZE
            block_number -= 1
        all_read_text = ''.join(reversed(blocks))
        return all_read_text.splitlines()[-total_lines_wanted:]


def ReadLargeFileDo(sFileName, doSth):
    """
        从 sFileName 读取数据，遍历每行数据调用 doSth
        doSth(iLineNo,sLine) -> sAction
        sAction: BREAK=中断，其余继续
    """
    with open(sFileName,"r") as f:
        iLineNo = -1
        for sLine in f: # 等价于 iter(f):   #[iStartIdx:]:这种写法不行
            iLineNo += 1
            if doSth(iLineNo,sLine.strip())=="BREAK": break


def GetFileSizeModTime(sFileName):
    # 得到指定文件的长度和修改时间
    import os
    try:
        s = os.stat(sFileName)
    except Exception as e:
        PrintTimeMsg('GetFileSizeModTime.stat(%s)=%s!' % (sFileName, str(e)))
        return 0,'YYYYMMDD-hhnnss'
    return s.st_size, GetUnixTimeLocal(s.st_mtime)

# -------------------------------
if __name__ == "__main__":
    print('__file__',__file__)
    print(GetSrcParentPath('.'))
    # cmLog = GetCriticalMsgLog('log@'+__file__) # 取源码文件目录
    # cmLog.log('Test','test')
    print(GetCurrentTime())
    tmNow = time.time()
    print(tmNow, GetUnixTimeLocal(tmNow))
    print("GetCurrentTimeMS()=",GetCurrentTimeMS(-10))
    s = u"\u7535\u8111-PC"
    print(s)
    PrintTimeMsg(s)
    if IsPython3():
        PrintTimeMsg(s.encode('utf-8'))
        print(s.encode('utf-8'))
        print(s.encode('utf-8').decode('utf-8'))
    else:
        PrintTimeMsg(s.decode('utf-8'))
        PrintTimeMsg(s.decode('utf-8').encode('utf-8'))
