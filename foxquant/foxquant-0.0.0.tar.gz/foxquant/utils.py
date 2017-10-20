# coding=utf-8

import datetime
import numpy as np


def to_date_str_fmt(date, fmt):
    """
    转换为日期字符串
    :param date:
    :param fmt:
    :return:
    """
    if date is None:
        return ""

    date = to_date_object(date)
    return date.strftime(fmt)


def to_date_str(date):
    """转换为日期字符串 %Y-%m-%d
    :param date:
    :return:
    """
    return to_date_str_fmt(date, '%Y-%m-%d')


def to_date_str_short(date):
    """转换为日期字符串 %Y-%m-%d
    :param date:
    :return:
    """
    return to_date_str_fmt(date, '%Y%m%d')


def to_date_object(date):
    """
    转换对象为日期对象
    :param date:
    :return:
    """
    if date is None:
        return None

    if isinstance(date, str):
        n = len(date)
        if 8 == n:
            fmt = '%Y%m%d'
        elif 10 == n:
            pos = date.find('/')
            if -1 == pos:
                fmt = '%Y-%m-%d' if 4 == date.find('-') else '%m-%d-%Y'
            elif 4 == pos:
                fmt = '%Y/%m/%d'
            else:
                fmt = '%m/%d/%Y'
        else:
            fmt = '%Y-%m-%d %H:%M:%S'
        date = datetime.datetime.strptime(date, fmt)

    if isinstance(date, np.datetime64):
        date = datetime.datetime.fromtimestamp(date.astype('O') / 1e9)

    if not isinstance(date, datetime.date):
        raise TypeError('date type error!' + str(date))
    return date
