#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import datetime
import re
import sys
import time

import six

from joker.cast import want_unicode


def eazy_date(x):
    """  
    >>> eazy_date(0)
    datetime.date(2017, 5, 5) 
    >>> eazy_date('today')
    datetime.date(2017, 5, 5) 
    
    >>> eazy_date(-1)
    datetime.date(2017, 5, 4) 
    >>> eazy_date('yesterday')
    datetime.date(2017, 5, 4) 
    
    >>> eazy_date(1)
    datetime.date(2017, 5, 6) 
    >>> eazy_date('tomorrow')
    datetime.date(2017, 5, 6) 
    
    >>> eazy_date(datetime.date.today())
    datetime.date(2017, 5, 5) 
    >>> eazy_date(datetime.datetime.now())
    datetime.date(2017, 5, 5) 
    
    >>> eazy_date('20170505')
    datetime.date(2017, 5, 5) 
    >>> eazy_date('2017-05-06')
    datetime.date(2017, 5, 6) 
    >>> eazy_date('05-06')
    datetime.date(2017, 5, 6) 
    >>> eazy_date('0506')
    datetime.date(2017, 5, 6) 
    
    :param x: 
    :return: a datetime.date instance
    """
    day = datetime.timedelta(days=1)
    today = datetime.date.today()
    if isinstance(x, int):
        return today + x * day
    elif isinstance(x, datetime.date):
        return x
    elif isinstance(x, datetime.datetime):
        return x.date()
    elif isinstance(x, six.string_types):
        x = want_unicode(x).lower()
    else:
        t = x.__class__.__name__
        raise TypeError('cannot convert type {} to date'.format(t))

    if x == 'today':
        return eazy_date(0)
    if x == 'yesterday':
        return eazy_date(-1)
    if x == 'tomorrow':
        return eazy_date(1)

    if re.match(r'\d{8}$', x):
        return datetime.datetime.strptime(x, '%Y%m%d').date()

    if re.match(r'\d{4}$', x):
        x = '{}{}'.format(today.year, x)
        return datetime.datetime.strptime(x, '%Y%m%d').date()

    if re.match(r'\d{4}-\d{1,2}-\d{1,2}$', x):
        return datetime.datetime.strptime(x, '%Y-%m-%d').date()

    if re.match(r'\d{1,2}-\d{1,2}$', x):
        x = '{}-{}'.format(today.year, x)
        return datetime.datetime.strptime(x, '%Y-%m-%d').date()
    raise ValueError('unknow date format')


def date_range(start, stop=0, step=1):
    """
    >>> list(date_range(-3, 0))  # last 3 days
    [datetime.date(2017, 5, 2),
     datetime.date(2017, 5, 3),
     datetime.date(2017, 5, 4)]
     
    :param start: 
    :param stop: 
    :param step: 
    :return: 
    """
    start = eazy_date(start)
    stop = eazy_date(stop)
    delta = datetime.timedelta(days=step)
    while (start - stop).total_seconds() * step < 0:
        yield start
        start += delta


class Timer(object):
    def __init__(self, name=''):
        self.name = name

    def __enter__(self):
        self.time = time.time()
        return self

    def __exit__(self, typ, value, traceback):
        interval = time.time() - self.time
        p = 'Timer {}'.format(self.name) if self.name else 'Timer'
        msg = '{}: {} sec'.format(p, interval)
        print(msg, file=sys.stderr)


class TimeMachine(object):
    def __init__(self, start=None, speed=None):
        self._initpoint = datetime.datetime.now()
        self._imaginary = not (start or speed)
        self._start = start or self._initpoint
        self._speed = speed or 1.

    def now(self):
        if not self._imaginary:
            return datetime.datetime.now()
        delta = datetime.datetime.now() - self._initpoint
        return self._start + delta * self._speed

    @staticmethod
    def convert_time_to_timedelta(t):
        return datetime.timedelta(
            hours=t.hour, minutes=t.minute, seconds=t.second,
            microseconds=t.microsecond
        )


class TimeSlicer(TimeMachine):
    EPOCH = datetime.datetime(1970, 1, 1)

    def __init__(self, start=None, speed=None, ts_size=600):
        super(TimeSlicer, self).__init__(start, speed)
        self._ts_delta = datetime.timedelta(seconds=ts_size)

    def get_current_timeslice(self, relative=True):
        dt = self.now()
        return self.convert_datetime_to_timeslice(dt, relative=relative)

    @staticmethod
    def guess_slice_size(ts):
        """
        assuming slice size a multiple of 60
        :param ts:
        :return:
        """
        t = time.time()
        return int(round(t / ts / 60.)) * 60

    def convert_timeslice_to_time(self, ts):
        dt = self.EPOCH + self._ts_delta * ts
        return dt.time()

    def convert_timeslice_to_datetime(self, ts, relative=True):
        """
        If relative is true, given ts is considered relative to
        00:00:00 of today.

        :param ts: an integer, serial number of timeslice
        :param relative: bool
        :return: a datetime instance
        """
        if not relative:
            return self.EPOCH + self._ts_delta * ts
        d = self.now().date()
        t = self.convert_timeslice_to_time(ts)
        return datetime.datetime.combine(d, t)

    def convert_time_to_timeslice(self, t):
        delta = self.convert_time_to_timedelta(t)
        # use .total_seconds to be compat with python 2.x
        return int(delta.total_seconds() / self._ts_delta.total_seconds())

    def convert_datetime_to_timeslice(self, dt, relative=True):
        if relative:
            return self.convert_time_to_timeslice(dt.time())
        delta = dt - self.EPOCH
        # use .total_seconds to be compat with python 2.x
        return int(delta.total_seconds() / self._ts_delta.total_seconds())

