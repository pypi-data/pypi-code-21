# -*- coding: utf-8 -*-
#系统相关函数
import datetime

def get_exec_time(func,*arg,**argv):
    '''返回函数的执行时间'''
    startTime = datetime.datetime.now()
    func(*arg,**argv)
    endTime = datetime.datetime.now()
    return (endTime-startTime).total_seconds()