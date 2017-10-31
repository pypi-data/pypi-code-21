#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/8/9 16:26"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
定时运行特定任务，任务直接配置在代码中。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs
# pip install schedule
"""
import sys
import time
from .WyfPublicFuncs import PrintTimeMsg, PrintAndSleep, WyfAppendToFile
import schedule
import subprocess

gDictTaskSchedules = {  # 定时任务配置，@开头的key是示例配置
    '@week': {  # 每周一 10:30 或 每周四 22:45
        'unit': 'week',
        'at': [('monday', '10:30'), ('thursday', '22:45')],
        'do': '#ping www.qq.com',
    },
    '@day': {  # 每天 10:30/22:25 运行
        'unit': 'day',
        'at': ['10:30', '22:25'],
        'do': '#ping www.qq.com',
    },
    '@hour':{  # 每小时 :00/:30 运行
        'unit': 'hour',
        'at': [':00', ':30'],
        'do': '#ping www.qq.com',
    },
    '@minute': {  # 每 3 分钟运行
        'unit': 'minute',
        'every': 1,  # 3,
        'do': '#ping www.qq.com >> logPing.tr 2>&1',
        # 'do': 'start ping www.qq.com >> logPing.tr 2>&1',
    },
    'minute': {  # 每 3 分钟运行
        'unit': 'minute',
        'every': 1,  # 3,
        'do': 'ping www.qq.com >> logPing.tr 2>&1',
    },
}


class CRunCronTask:
    # 定时任务管理，推荐不等待任务执行结束的配置
    # 这里没有对任务执行时的系统资源和执行耗时进行判断。
    def __init__(self, sTaskLogFN):
        self.sTaskLogFN = sTaskLogFN  # 定时任务执行日志文件
        PrintTimeMsg('CRunCronTask.sTaskLogFN=%s' % self.sTaskLogFN)
        self.bPrintWaitInfo = True   # 默认首次打印等待信息

    def AddAllScheduleTask(self, dictTaskSchedules):
        # 按照配置字典增加定时任务
        for sKey,dictTask in dictTaskSchedules.items():
            if not sKey.startswith('@'):
                self.AddOneScheduleTask(sKey, dictTask, None)

    def AddOneScheduleTask(self, sTaskKey, dictTask, cbFunc=None):
        if cbFunc is None:
            cbFunc = self.CheckExecJob
        sDo = dictTask.get('do', '')
        sUnit = dictTask.get('unit', '')
        if sUnit == 'minute':
            iT = dictTask.get('every', 1)
            schedule.every(iT).minutes.do(cbFunc, sDo)
        elif sUnit == 'hour':
            lsAt = dictTask.get('at', [])
            if lsAt:
                for sAt in lsAt:
                    schedule.every().hour.at(sAt).do(cbFunc, sDo)
            else:
                schedule.every().hour.do(cbFunc, sDo)
        elif sUnit == 'day':
            lsAt = dictTask.get('at', [])
            if lsAt:
                for sAt in lsAt:
                    schedule.every().day.at(sAt).do(cbFunc, sDo)
            else:
                schedule.every().day.do(cbFunc, sDo)
        elif sUnit == 'week':
            lsAt = dictTask.get('at', [])
            if lsAt:
                for sWeekDay,sAt in lsAt:
                    getattr(schedule.every(), sWeekDay).at(sAt).do(cbFunc, sDo)
            else:
                schedule.every().week.do(cbFunc, sDo)
        PrintTimeMsg('AddOneScheduleTask(%s)=%s=' % (sTaskKey, sDo))

    def CheckExecJob(self, sCmd):
        # 检查并执行任务
        # sExecMsg = ''
        if sCmd.startswith('#'):
            sExecMsg = "CheckExecJob(%s)=NoRun!" % sCmd
        else:
            sExecMsg = self.ExecCmdBySystem(sCmd)
            # sExecMsg = self.ExecCmdByPopen(sCmd)
        PrintTimeMsg(sExecMsg)
        WyfAppendToFile(self.sTaskLogFN, sExecMsg)
        self.bPrintWaitInfo = True  # 每次执行命令后打印

    @staticmethod
    def ExecCmdBySystem(sCmd):
        # 通过 system 调用命令
        import os
        PrintTimeMsg("ExecCmdBySystem(%s)..." % sCmd)
        tmBegin = time.time()
        iRet = os.system(sCmd)
        tmLast = time.time() - tmBegin
        sExecMsg = "ExecCmdBySystem.consume=%.2fs(%s)=%s=" % (tmLast, sCmd, iRet)
        return sExecMsg

    @staticmethod
    def ExecCmdByPopen(sCmd):
        # 通过 Popen 调用命令
        import psutil
        PrintTimeMsg("ExecCmdByPopen(%s)..." % sCmd)
        tmBegin = time.time()
        # iRet = os.system(sCmd)
        pid = psutil.Popen(sCmd)
        # 这里需要对 psutil.Popen(sCmd, stdout=self.fdOut,stderr=self.fdErr, shell=self.bShellPopen)
        # 标准输出等 进行处理。
        # 这样就需要增加配置文件，暂时不进行处理了。
        tmLast = time.time() - tmBegin
        sExecMsg = "ExecCmdByPopen.consume=%.2fs(%s)=%s=" % (tmLast, sCmd, pid)
        return sExecMsg

    def LoopForSchedulePending(self):
        # 循环等待任务执行
        self.bPrintWaitInfo = True
        while True:
            schedule.run_pending()
            iSec = int(schedule.idle_seconds())
            sNextRun = 'SchedulePending.Wait(%s)=%ss' % (schedule.next_run(), iSec)
            if iSec > 3600:
                bPrint = (iSec % 3600 == 0)
            elif iSec > 1800:
                bPrint = (iSec % 600 == 0)
            elif iSec > 120:
                bPrint = (iSec % 60 == 0)
            else:
                bPrint = (iSec % 10 == 0)
            PrintAndSleep(1, sNextRun, bPrint or self.bPrintWaitInfo)
            self.bPrintWaitInfo = False


def mainCRunCronTask():
    global gDictTaskSchedules
    o = CRunCronTask('CronTask.log')
    o.AddAllScheduleTask(gDictTaskSchedules)
    o.LoopForSchedulePending()


# --------------------------------------
if __name__ == '__main__':
    mainCRunCronTask()
