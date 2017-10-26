#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import pycoraldb

client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5166')
client.login("test", "123456789")

def test1():
    t1 = datetime.datetime.now()
    rs2 = client.getBar('510300.SH', beginDate=20160108, endDate=20160108)
    t2 = datetime.datetime.now()
    print 'query spend %s: size = %s' % (t2-t1, len(rs2))

def test2():
    t1 = datetime.datetime.now()
    rs2 = client.getBar('510300.SH', beginDate=20160108, endDate=20160121)
    t2 = datetime.datetime.now()
    print 'query spend %s: size = %s' % (t2-t1, len(rs2))

def test3():
    t1 = datetime.datetime.now()
    cycle = pycoral.S
    rs = client.getBar('000001.SZ', beginDate=20160108, endDate=20160121, cycle=cycle, holo=True)
    t2 = datetime.datetime.now()
    print 'query spend %s: size = %s' % (t2-t1, len(rs))

if __name__ == '__main__':
    test1()
