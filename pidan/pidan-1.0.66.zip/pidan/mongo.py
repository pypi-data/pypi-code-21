# -*- coding: utf-8 -*-
#与mongodb相关的函数
import time

def timestamp_from_objectid(objectid):
    '''从objectid获取时间戳'''
    result = 0
    try:
        result = time.mktime(objectid.generation_time.timetuple())
    except:
        pass
    return result