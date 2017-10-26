#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午5:03
# @Author  : Hou Rong
# @Site    : 
# @File    : Date.py
# @Software: PyCharm
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/15 下午3:52
# @Author  : Hou Rong
# @Site    :
# @File    : DateRange.py
# @Software: PyCharm
import datetime

DATE_FORMAT = "%Y-%m-%d"


def date_range(start_date, end_date, day_step=1, ignore_days=0):
    dates = []
    dt = datetime.datetime.strptime(start_date, DATE_FORMAT)
    dt += datetime.timedelta(ignore_days)
    date = dt.strftime(DATE_FORMAT)
    yield date
    while date < end_date:
        dates.append(date)
        dt += datetime.timedelta(day_step)
        date = dt.strftime(DATE_FORMAT)
        yield date


def date_until(end_date, day_step=1, ignore_days=0):
    dt = datetime.datetime.now()
    start_date = dt.strftime(DATE_FORMAT)
    for i in date_range(start_date=start_date, end_date=end_date, day_step=day_step, ignore_days=ignore_days):
        yield i


def date_takes(take_days, day_step=1, ignore_days=0):
    dt = datetime.datetime.now()
    for _i in range(ignore_days, take_days + ignore_days, day_step):
        yield (dt + datetime.timedelta(_i)).strftime(DATE_FORMAT)
