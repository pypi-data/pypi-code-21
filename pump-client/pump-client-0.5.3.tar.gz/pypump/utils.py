# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from dateutil.parser import parse as dateparse

from .compat import string_types, urlparse


def guess_ds_type(dsn):
    return urlparse.urlparse(dsn).scheme


def map_udf(udf):
    return {
        'day': 'day',
        'daily': 'day',
        'week': 'week',
        'weekly': 'week',
        'month': 'month',
        'monthly': 'month',
        'year': 'year',
        'yearly': 'year'
    }.get(udf, udf)


def map_order_dir(direction):
    return {
        '+': '+',
        '-': '-',
        'asc': '+',
        'desc': '-'
    }[direction]


def check_string_type(value):
    if not isinstance(value, string_types):
        raise ValueError('value must be string type')


def ensure_list(v):
    if isinstance(v, (list, set, tuple)):
        return list(v)
    return v is not None and [v] or []


def cast(value, typ):
    if isinstance(typ, type):
        typ = typ.__name__.lower()
    elif isinstance(typ, string_types):
        typ = typ.lower()
    else:
        typ = type(typ).__name__.lower()

    if typ in ['int', 'int32', 'int64', 'long', 'integer', 'bigint', 'smallint', 'tinyint', 'short']:
        return int(value)
    if typ in ['float', 'double', 'numeric', 'number', 'decimal', 'number(real)']:
        return float(value)
    if typ in [x for x in string_types] + ['varchar', 'string', 'char', 'text']:
        return str(value)
    if typ in ['datetime', 'timestamp']:
        return dateparse(value).strftime('%Y-%m-%d %H:%M:%S')
    if typ in ['date']:
        return dateparse(value).strftime('%Y-%m-%d')
    return value


def extract_func_field(s):
    """Extract function name (if exists) and field name"""
    x = re.match('([a-z]+)\((.+)\)', s)
    if x is not None:
        func, field = x.groups()
    else:
        func, field = None, s
    return func, field


def make_alias(func, field):
    return '{}__{}'.format(func, field)


def get_col_name(metric_or_groupby):
    """根据 Pump 的规则, 计算结果集中的列名。

    :param metric_or_groupby: metric (dict) 或 groupby 的字段(string 或 tuple)
    :return: 列名
    :rtype: basestring

    >>> metric = {'field': 'id', 'aggregation': 'max', 'alias': 'max_id'}
    >>> get_col_name(metric)
    max_id

    >>> metric = {'field': 'id', 'aggregation': 'max', 'alias': ''}
    >>> get_col_name(metric)
    max__id

    >>> metric = {'field': 'id', 'aggregation': 'max'}
    >>> get_col_name(metric)
    max__id

    >>> groupby = 'daily(created_at)'
    >>> get_col_name(groupby)
    day__created_at

    >>> groupby = 'day(created_at)'
    >>> get_col_name(groupby)
    day__created_at

    >>> groupby = ('created_at', 'weekly')
    >>> get_col_name(groupby)
    week__created_at
    """
    if isinstance(metric_or_groupby, string_types):
        udf, field = extract_func_field(metric_or_groupby)
        if udf:
            return make_alias(map_udf(udf), field)
        return field
    elif isinstance(metric_or_groupby, tuple):
        # metric: (field, aggregation)
        # groupby: (field, udf)
        field, func = metric_or_groupby[:2]
        return make_alias(map_udf(func), field)
    elif isinstance(metric_or_groupby, dict):
        # metric: {"field": field, "aggregation": agg, "alias": alias}
        if metric_or_groupby.get('alias'):
            return metric_or_groupby['alias']
        agg = metric_or_groupby.get('aggregation')
        if agg:
            return make_alias(agg, metric_or_groupby['field'])
        return metric_or_groupby['field']


def split_range_bins(points):
    """根据每个点，生成 pump 兼容的多个区间.

    :param points: [0, 10, 20, 40]
    :return: [[0, 10], [10, 20], [20, 40], [40, None]]

    >>> split_range_bins([0, 10, 20, 40])
    [[0, 10], [10, 20], [20, 40], [40, None]]
    """
    lst = list(points)
    lst.append(None)
    return zip(lst[:-1], lst[1:])


def format_bins_label(bins):
    """格式化区间

    >>> format_bins_label([0, 10])
    '0~10'

    >>> format_bins_label([0])
    '>= 0'

    >>> format_bins_label([0, None])
    '>= 0'

    >>> format_bins_label([None, 10])
    '< 10'
    """
    if len(bins) == 1:
        return '>= {}'.format(bins[0])
    if bins[0] is None:
        return '< {}'.format(bins[1])
    if bins[1] is None:
        return '>= {}'.format(bins[0])
    return '{}~{}'.format(bins[0], bins[1])


def get_range_col_name(values):
    """根据区间列表（[[0, 10], [10, 20]]）或区间断点列表（[0, 10, 20]）获取 pump 返回的对应列名

    >>> get_range_col_name([0, 10, 20])
    ['0~10', '10~20', '>= 20']
    
    >>> get_range_col_name([[0, 10], [10, 20], [20, None]])
    ['0~10', '10~20', '>= 20']
    
    >>> get_range_col_name([[0, 10], [10, 20], [20]])
    ['0~10', '10~20', '>= 20']
    
    >>> get_range_col_name([[0, 10], [10, 20], [2]])
    ['0~10', '10~20', '>= 2']
    
    >>> get_range_col_name([[0, 10], [10, 20]])
    ['0~10', '10~20']
    """
    if isinstance(values[0], (list, tuple)):
        # 区间列表
        return map(format_bins_label, values)
    # 区间里的断点
    return map(format_bins_label, split_range_bins(values))
