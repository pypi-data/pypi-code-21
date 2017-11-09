#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function
import math


def floor(number):
    return int(math.floor(number))


def ceil(number):
    return int(math.ceil(number))


def overlap_size(v1, v2, u1, u2):
    """
    Calculate overlap size of intervals (v1, v2) and (u1, u2)
    """
    alen = abs(v1 - v2)
    blen = abs(u1 - u2)
    wide = max(v1, v2, u1, u2) - min(v1, v2, u1, u2)
    return alen + blen - wide


def grid_align(v, unitsize):
    unitsize = float(unitsize)
    v = round(v / unitsize) * unitsize
    if round(unitsize) == unitsize:
        return int(v)
    return v


def metric_prefix(number):
    """
    >>> metric_prefix(10 ** 11) 
    (100.0, 'G', 9)
    >>> metric_prefix(.1 ** 5)
    (10.000000000000002, 'u', -6)
    
    :param number: 
    :return: (a, prefix, b)
    number = a * (10 ^ b)
    """
    ix, prefix = 0, ''
    if number >= 1000:
        for ix, prefix in enumerate('kMGTPEZY'):
            number /= 1000.
            if number <= 1000:
                return number, prefix, 3 * (1 + ix)
        return number, prefix, 3 * (1 + ix)
    if number <= .001:
        for ix, prefix in enumerate('munp'):
            number *= 1000.
            if number >= 1:
                return number, prefix, -3 * (1 + ix)
        return number, prefix, -3 * (1 + ix)
    return number, '', 0


def human_filesize(number):
    """
    Human readable file size unit
    :param number: how many bytes
    :return: (num, unit)
    """
    units = ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    for unit in units:
        if number < 10000 or unit == "YB":
            return number, unit
        else:
            number = number / 1024.0
            # to next loop, no return!
