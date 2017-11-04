# All of generic map functions are here
# Must to add unittest

import time
from datetime import datetime

from .h import *


def m_str_to_float(seq):
    """
    transform str list to float list
    :param seq: str list
    :return: list, float list or []
    """

    def _type_cast(x):
        try:
            x = float(x) if x not in ('', None, ) else None
        except ValueError:
            pass

        return x

    # list(map(lambda x: float(x) if x else 0.0, seq))
    return list(map(_type_cast, seq))


def m_de_weight_of_list(seq):
    """
    de-weight for list, for example [1, 1, 2] return [1, 2]
    :param seq: list
    :return: list
    """

    return list(set(seq))


def m_timestamp_to_month(seq):
    """
    transform Unix timestamp(int or str) list to month(int) list
    :param seq: list of Unix timestamp
    :return: list of month
    """
    def _inner(x):
        if isinstance(x, str):
            x = x[:10]

        return time.localtime(int(x)).tm_mon

    return list(map(_inner, seq))


def m_timestamp_to_hour(seq):
    """
    transform Unix timestamp(int or str) list to hour(int) list
    :param seq: list of Unix timestamp
    :return: list of int
    """
    def _inner(x):
        if isinstance(x, str):
            x = x[:10]

        return time.localtime(int(x)).tm_hour

    return list(map(_inner, seq))


def m_cut_out_before_n(seq, before_n=7):
    """
    get month of string datetime
    :param seq: str list
    :param before_n: retain the numbers of before list items
    :return: list
    string datetime format: 2016-10-01 00:17:17 result 2016-10
    """

    return list(map(lambda d: d[:before_n] if isinstance(d, str) else d, seq))


def m_one_list_to_n(seq, chunk_size):
    """
    按照chunk_size大小将一个list拆分成多个, 缺失填充None
    :param seq, input data list,
    :param chunk_size, sub list size
    :return list, big list contains len(seq)/chunk_size+1 sub tuple
    """
    return list(h_chunk_list(seq, chunk_size))


def m_transform_by_key(seq):
    """ 按照key分组，并返回相同分组的最大值构成的列表
        如：[('a', 2000), ('b', 3000), ('a', 3000)]  -> [3000, 3000]
    """
    group_by_key = {}

    for item in seq:
        if item[0] not in group_by_key:
            group_by_key[item[0]] = [item[1]]
            continue

        group_by_key[item[0]].append(item[1])

    return [max(v) for v in group_by_key.values()]


def m_divided_by(seq, divisor):
    """ 被指定数除，默认为1 """
    return list(map(lambda x: x / divisor, seq))


def m_cut_out_last_n(seq, last_n=4):
    """ 截取最后几位 """
    return list(map(lambda x: x[-last_n:] if isinstance(x, str) else x, seq))


def m_date_str_to_datetime(seq):
    """
    transform string date to datetime object, input can be string date or string datetime
    :param seq: list of date
    :return: list of datetime object
    """
    def _date_transformation(date_str):
        if isinstance(date_str, str) and ('0000-00-00' in date_str or date_str.strip() in ('', )):
            return None

        if isinstance(date_str, str):
            counter = Counter(date_str)
            if counter.get('-', 0) > 2:
                date_str = date_str[date_str.find('-')+1:]

        format_string = '%Y-%m-%d'
        if isinstance(date_str, str) and '-' not in date_str:
            format_string = '%Y%m%d'

        try:
            t = datetime.strptime(date_str, format_string)
        except ValueError:
            format_string = '%Y-%m-%d %H:%M:%S'
            if isinstance(date_str, str) and '-' not in date_str:
                format_string = '%Y%m%d%H%M%S'

            t = datetime.strptime(date_str, format_string)
        except TypeError:
            t = datetime.fromtimestamp(date_str)

        return t

    return list(map(_date_transformation, seq))


def m_str_to_int(seq):
    """
    transform sting digit to int
    :param seq: list of string
    :return: list of int
    """

    return list(map(lambda x: int(float(x)) if x else None, seq))


def m_timestamp_to_hour_slot(seq):
    """ 将时间戳转换成时间段

        1 夜话型 22:00-6:00
        2 工作型 9:00-12:00 and 14:00-19:00
        3 生活型 6:00-9:00 and 12:00-14:00 and 19:00-22:00
    """
    hour = m_timestamp_to_hour(seq)

    def h_interval_to_category(val):
        hour_slot_map = {
            '1': [22, 23, 0, 1, 2, 3, 4, 5, 6],
            '2': [9, 10, 11, 14, 15, 16, 17, 18],
            '3': [7, 8, 12, 13, 19, 20, 21]
        }

        for key, value in hour_slot_map.items():
            if val in value:
                return key

    return list(map(h_interval_to_category, hour))


def m_to_value(sequence, value):
    return list(map(lambda x: value, sequence))
