#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5166')
    # client = pycoraldb.CoralDBClient('coraldb://pfsh2:38021')
    client.login("test", "123456789")
    code = '600000.SH'
    beginDate = 20170103
    endDate = 20170103
    cycle = 0
    fields = "*"
    beginTime = 0
    endTime = 0
    holo = False
    holoInterval = 0
    t = datetime.datetime.now()
    rs = client.getBar(code, beginDate, endDate)
    print 'query ok in %s: size = %s' % (datetime.datetime.now() - t, len(rs))
    # for d in rs:
    #     print '[%s], date: %s, stamp: %s' % (d['timestamp'], d['date'], d['stamp'])
