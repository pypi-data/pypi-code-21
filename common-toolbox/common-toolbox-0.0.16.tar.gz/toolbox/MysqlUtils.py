#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午2:52
# @Author  : Hou Rong
# @Site    : 
# @File    : MysqlUtils.py
# @Software: PyCharm
import pymysql
from pymysql.cursors import DictCursor

__sql_dict = {
    'host': '',
    'user': ' ',
    'passwd': '',
    'charset': 'utf8',
    'db': ''
}


def get_data(table, source, step=10000):
    _conn = pymysql.connect(**__sql_dict)
    with _conn.cursor(cursor=DictCursor) as cursor:
        sql = 'select count(*) from {0} where source="{1}"'.format(table, source)
        cursor.execute(sql)
        total = list(cursor.fetchall()[0].values())[0]
        _count = 0
        for start in range(0, total + 1, step):
            sql = 'select * from {0} where source="{1}" limit {2},{3}'.format(table, source, start, step)
            cursor.execute(sql)
            for line in cursor.fetchall():
                yield line
                _count += 1
                if _count == 10000:
                    _count = 0
    _conn.close()
