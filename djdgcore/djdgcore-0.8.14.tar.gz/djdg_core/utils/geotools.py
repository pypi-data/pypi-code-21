#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/12/26
 """
from __future__ import unicode_literals, absolute_import
from math import radians, cos, sin, asin, sqrt
import Geohash


# 经度1，纬度1，经度2，纬度2 （十进制度数）
def haversine(lon1, lat1, lon2, lat2, ndigits=2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    v = c * r * 1000
    return round(v, ndigits)


LONGITUDE_UNIT = 360.0 / 2 ** 15
LATITUDE_UNIT = 180.0 / 2 ** 15
LONGITUDE_LENGTH_UNIT = haversine(0, 0, LATITUDE_UNIT, 0)
LATITUDE_LENGTH_UNIT = haversine(0, 0, 0, LATITUDE_UNIT)
GEOHASH_LENGTH = 6


# 按照范围查找目标点相邻的区域
def range_geohash(lon, lat, dist_range=3000):
    """
    :param lon:
    :param lat:
    :param dist_range:
    :return:
    """
    lon_blocks = max(1, int(dist_range / LONGITUDE_LENGTH_UNIT))
    lat_blocks = max(1, int(dist_range / LATITUDE_LENGTH_UNIT))
    if lon_blocks % 2:
        lon_blocks += 1
    if lat_blocks % 2:
        lat_blocks += 1
    lon_blocks, lat_blocks = lon_blocks / 2, lat_blocks / 2
    geohash_set = set()
    for i in xrange(lat_blocks + 1):
        for j in xrange(lon_blocks):
            geohash_set.add(
                Geohash.encode(lat, lon + (j + 1) * LONGITUDE_UNIT, GEOHASH_LENGTH)
            )
            geohash_set.add(
                Geohash.encode(lat, lon - (j + 1) * LONGITUDE_UNIT, GEOHASH_LENGTH)
            )
        if 0 == i:
            geohash_set.add(
                Geohash.encode(lat, lon, GEOHASH_LENGTH)
            )
        else:
            geohash_set.add(
                Geohash.encode(lat + i * LATITUDE_UNIT, lon, GEOHASH_LENGTH)
            )
            geohash_set.add(
                Geohash.encode(lat - i * LATITUDE_UNIT, lon, GEOHASH_LENGTH)
            )
    return list(geohash_set)


GEOHASH_PRECISION = 12


# 对经纬度进行编码，统一使用12位精度
def geohash_encode(lon, lat):
    return Geohash.encode(lat, lon, GEOHASH_PRECISION)


def geohash_decode(code):
    return Geohash.decode(code)