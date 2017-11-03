# encoding: utf-8

"""
convert.py

Created by Hywel Thomas on 2010-11-24.
Copyright (c) 2010 Hywel Thomas. All rights reserved.
"""

import inspect
import datetime
import time

import logging_helper
from timingsutil.timers import tz_adjust

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'

logging = logging_helper.setup_logging()

CONVERTER = u'converter'

DAYS = (u'Monday',
        u'Tuesday',
        u'Wednesday',
        u'Thursday',
        u'Friday',
        u'Saturday',
        u'Sunday')

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = DAYS


def datetime_to_epoch(dt=None):
    # TODO: Add better handling of timezones (e.g. using pytz)
    dt = dt if dt is not None else datetime.datetime.now()

    return (dt - datetime.datetime(1970, 1, 1)).total_seconds() - tz_adjust


def epoch_to_time(ep=None,
                  time_format=u'%d-%m-%y %H:%M:%S'):
    # TODO: Add handling of timezones (e.g. using pytz)
    if ep is None:
        ep = datetime_to_epoch(datetime.datetime.now())

    if ep > 9999999999:
        ep /= 1000

    return time.strftime(time_format, time.localtime(ep))


def string_to_time(timestring,
                   time_format=u'%H:%M'):
    # TODO: Add handling of timezones (e.g. using pytz)
    return datetime.datetime.strptime(timestring, time_format).time()


def day_of_week(ep = None):
    # TODO: Add handling of timezones (e.g. using pytz)
    if ep is None:
         ep = time.mktime(datetime.datetime.now().timetuple())
    if ep > 9999999999:
         ep = ep / 1000
    return DAYS[time.localtime(ep).tm_wday]


def next_day(day):
    return DAYS[(DAYS.index(day) + 1) % len(DAYS)]


def previous_day(day):
    return DAYS[(DAYS.index(day) - 1) % len(DAYS)]

if __name__ == u"__main__":
    assert next_day(u'Monday') == u'Tuesday'
    assert next_day(u'Sunday') == u'Monday'
    assert previous_day(u'Monday') == u'Sunday'
    assert previous_day(u'Sunday') == u'Saturday'


def get_datetime_conversion(datetime_format):
    # TODO: Add handling of timezones (e.g. using pytz)
    return {CONVERTER: epoch_to_time,
            u'time_format': datetime_format}
