#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging as log
import datetime

class UTC(datetime.tzinfo):
    """
    Coordinated Universal Time, UTC
    https://www.ietf.org/rfc/rfc3339.txt
    """
    def __init__(self, offset = 0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return self.__str__()
# 
    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)
    
    def __str__(self, *args, **kwargs):
        return "UTC +%02d" % (self._offset) if self._offset >= 0 else "UTC -%02d" % (-self._offset)


def rawDate():
    return int(datetime.datetime.now().strftime('%Y%m%d'))


def rawDateText(rDate=None):
    if rDate is None:
        rDate = int(datetime.datetime.now().strftime('%Y%m%d'))
    return '%04d-%02d-%02d' % (rDate/10000, rDate%10000/100, rDate%100)


def rawTime():
    s = datetime.datetime.now().strftime('%H%M%S%f')
    tm = long(s[:-3])
    return tm


def rawTimeText(rTime=None):
    if rTime is None:
        return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    else:
        return '%02d:%02d:%02d.%03d' % (rTime/10000000, rTime%10000000/100000, rTime%100000/1000, rTime%1000)

def addRawTime(rTime, ms):
    _ms = (rTime / 10000000) * 3600000 + (rTime % 10000000 / 100000) * 60000 + (rTime % 100000 / 1000) * 1000 + rTime % 1000
    _ms += ms
    return _ms / 3600000 * 10000000 + _ms % 3600000 / 60000 * 100000 + _ms % 60000 / 1000 * 1000 + _ms % 1000


def subRawTime(t1, t2):
    ms1 = (t1 / 10000000) * 3600000 + (t1 % 10000000 / 100000) * 60000 + (t1 % 100000 / 1000) * 1000 + t1 % 1000
    ms2 = (t2 / 10000000) * 3600000 + (t2 % 10000000 / 100000) * 60000 + (t2 % 100000 / 1000) * 1000 + t2 % 1000
    return ms1 - ms2


if __name__ == '__main__':
    pass