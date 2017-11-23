#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-21 04:31:24
# Author: xujif
# -----
# Last Modified: 2017-08-30 01:21:42
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###


def js_float(s: str):
    if s == 'NaN' or s == '':
        return 0
    else:
        return float(s)


def js_int(s: str):
    if s == 'NaN' or s == '':
        return 0
    else:
        return int(s)


def fix_round(num, pos):
    import math
    p = math.pow(10, pos)
    return math.ceil(num * p) / p


def humen_read_number(num):
    if (num > 1000000000000):
        return str(fix_round(num / 1000000000000, 2)) + '万亿'
    elif(num > 100000000):
        return str(fix_round(num / 100000000, 2)) + '亿'
    elif(num > 10000000):
        return str(fix_round(num / 10000000, 2)) + '千万'
    elif(num > 10000):
        return str(fix_round(num / 10000, 2)) + '万'
    else:
        return str(fix_round(num, 2))


def code_to_market(code):
    code = str(code)
    if len(code) == 6:
        return 'sh' if code[0] in ['5', '6', '9'] else 'sz'
    elif len(code) == 8:
        return code[0:2]
    else:
        return code


def code_to_symbol(code):
    code = str(code)
    if len(code) == 6:
        return code_to_market(code) + code
    else:
        return code


def symbol_to_code(code):
    code = str(code)
    if len(code) == 8:
        return code[2:8]
    else:
        return code
