#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/7 11:42"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
对调用命令函数进行简化封装。
参考 [Python subprocess.Popen Examples](https://www.programcreek.com/python/example/50/subprocess.Popen)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from WyfPublicFuncs import PrintTimeMsg, PrintInline
import time
import subprocess as sp


def ExecCmdWaitByPopen(sCmd):
    # 通过 Popen 调用命令，等待模式
    # import psutil
    PrintTimeMsg("ExecCmdWaitByPopen(%s)..." % sCmd)
    tmBegin = time.time()
    # iRet = os.system(sCmd)
    p = sp.Popen(sCmd, stdout=sp.PIPE, stderr=sp.STDOUT)
    while True:
        sLine = p.stdout.readline()
        if sLine == "":
            break
        sLine = sLine.strip()
        if isinstance(sLine, unicode):
            PrintInline('  %s\n' % sLine)
        else:
            PrintInline('  %s\n' % sLine.decode('gbk'))  # 可以不要.encode('utf8')
    out, err = p.communicate()  # 阻塞，直至子进程结束
    PrintTimeMsg("ExecCmdWaitByPopen.out=(%s)" % out)
    PrintTimeMsg("ExecCmdWaitByPopen.err=(%s)" % err)
    tmLast = time.time() - tmBegin
    PrintTimeMsg("ExecCmdWaitByPopen(%s)=(%s).Consume=%.2fs!" % (sCmd, p.returncode, tmLast))
    return p.returncode


def ExecCmdWaitOutErrByPopen(sCmd):
    # 通过 Popen 调用命令，等待模式, 并返回标准输出和标准错误输出结果
    # import psutil
    PrintTimeMsg("ExecCmdWaitByPopen(%s)..." % sCmd)
    tmBegin = time.time()
    # p = sp.Popen(sCmd, stdout=sp.PIPE, stderr=sp.STDOUT)
    p = sp.Popen(sCmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)  # echo 命令要求 shell=True
    lsOut = p.stdout.readlines()
    lsErr = p.stderr.readlines()
    out, err = p.communicate()  # 阻塞，直至子进程结束
    # PrintTimeMsg("ExecCmdWaitByPopen.out=(%s)" % out)
    # PrintTimeMsg("ExecCmdWaitByPopen.err=(%s)" % err)
    if lsOut:
        PrintTimeMsg("    lsOut={%s}" % ''.join(lsOut))
    if lsErr:
        PrintTimeMsg("    lsErr={%s}" % ''.join(lsErr))
    tmLast = time.time() - tmBegin
    PrintTimeMsg("ExecCmdWaitByPopen(%s)=(%s).Consume=%.2fs!" % (sCmd, p.returncode, tmLast))
    return p.returncode, lsOut, lsErr


def tryExecCmdByPopen():
    # ExecCmdWaitByPopen('ping 127.0.0.1')
    # ExecCmdWaitByPopen('ping www.qq.com')
    # ExecCmdWaitByPopen('ping www.qq.com -t')
    # ExecCmdWaitOutErrByPopen('ping www.qq.com')
    ExecCmdWaitOutErrByPopen('echo www.qq.com')
    ExecCmdWaitOutErrByPopen('echo www.\nqq.com 1>&2')


# --------------------------------------
if __name__ == '__main__':
    tryExecCmdByPopen()
