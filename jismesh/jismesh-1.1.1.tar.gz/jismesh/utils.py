#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import sys
if sys.version_info.major < 3:
    import functools32 as functools
else:
    import functools

# unit in degree of latitude and longitude for each mesh level. 
unit_lat_lv1 = functools.lru_cache(1)(lambda: 2/3)
unit_lon_lv1 = functools.lru_cache(1)(lambda: 1)
unit_lat_lv2 = functools.lru_cache(1)(lambda: unit_lat_lv1()/8)
unit_lon_lv2 = functools.lru_cache(1)(lambda: unit_lon_lv1()/8)
unit_lat_5000 = functools.lru_cache(1)(lambda: unit_lat_lv2()/2)
unit_lon_5000 = functools.lru_cache(1)(lambda: unit_lon_lv2()/2)
unit_lat_2000 = functools.lru_cache(1)(lambda: unit_lat_lv2()/5)
unit_lon_2000 = functools.lru_cache(1)(lambda: unit_lon_lv2()/5)
unit_lat_lv3 = functools.lru_cache(1)(lambda: unit_lat_lv2()/10)
unit_lon_lv3 = functools.lru_cache(1)(lambda: unit_lon_lv2()/10)
unit_lat_lv4 = functools.lru_cache(1)(lambda: unit_lat_lv3()/2)
unit_lon_lv4 = functools.lru_cache(1)(lambda: unit_lon_lv3()/2)
unit_lat_lv5 = functools.lru_cache(1)(lambda: unit_lat_lv4()/2)
unit_lon_lv5 = functools.lru_cache(1)(lambda: unit_lon_lv4()/2)
unit_lat_lv6 = functools.lru_cache(1)(lambda: unit_lat_lv5()/2)
unit_lon_lv6 = functools.lru_cache(1)(lambda: unit_lon_lv5()/2)
unit_lat_100 = functools.lru_cache(1)(lambda: unit_lat_lv3()/10)
unit_lon_100 = functools.lru_cache(1)(lambda: unit_lon_lv3()/10)

def to_meshcode(lat, lon, level):
    """緯度経度から指定次の地域メッシュコードを算出する。
    
    Args:
        lat: 世界測地系の緯度(度単位)
        lon: 世界測地系の経度(度単位)
        level: 地域メッシュコードの次数 
                1次:1
                2次:2
                5倍:5000
                2倍:2000
                3次:3
                4次:4
                5次:5
                6次:6
                100メートル:100
    Return:
        指定次の地域メッシュコード

    """

    # reminder of latitude and longitude by its unit in degree of mesh level.
    rem_lat_lv0 = lambda lat: lat
    rem_lon_lv0 = lambda lon: lon % 100
    rem_lat_lv1 = lambda lat: rem_lat_lv0(lat) % unit_lat_lv1()
    rem_lon_lv1 = lambda lon: rem_lon_lv0(lon) % unit_lon_lv1()
    rem_lat_lv2 = lambda lat: rem_lat_lv1(lat) % unit_lat_lv2()
    rem_lon_lv2 = lambda lon: rem_lon_lv1(lon) % unit_lon_lv2()
    rem_lat_5000 = lambda lat: rem_lat_lv2(lat) % unit_lat_5000()
    rem_lon_5000 = lambda lon: rem_lon_lv2(lon) % unit_lon_5000()
    rem_lat_2000 = lambda lat: rem_lat_lv2(lat) % unit_lat_2000()
    rem_lon_2000 = lambda lon: rem_lon_lv2(lon) % unit_lon_2000()
    rem_lat_lv3 = lambda lat: rem_lat_lv2(lat) % unit_lat_lv3()
    rem_lon_lv3 = lambda lon: rem_lon_lv2(lon) % unit_lon_lv3()
    rem_lat_lv4 = lambda lat: rem_lat_lv3(lat) % unit_lat_lv4()
    rem_lon_lv4 = lambda lon: rem_lon_lv3(lon) % unit_lon_lv4()
    rem_lat_lv5 = lambda lat: rem_lat_lv4(lat) % unit_lat_lv5()
    rem_lon_lv5 = lambda lon: rem_lon_lv4(lon) % unit_lon_lv5()
    rem_lat_lv6 = lambda lat: rem_lat_lv5(lat) % unit_lat_lv6()
    rem_lon_lv6 = lambda lon: rem_lon_lv5(lon) % unit_lon_lv6()
    rem_lat_100 = lambda lat: rem_lat_lv3(lat) % unit_lat_100()
    rem_lon_100 = lambda lon: rem_lon_lv3(lon) % unit_lon_100()

    def meshcode_lv1(lat, lon):
        ab = int(rem_lat_lv0(lat) / unit_lat_lv1())
        cd = int(rem_lon_lv0(lon) / unit_lon_lv1())
        return str(ab) + str(cd)
    
    def meshcode_lv2(lat, lon):
        e = int(rem_lat_lv1(lat) / unit_lat_lv2())
        f = int(rem_lon_lv1(lon) / unit_lon_lv2())
        return meshcode_lv1(lat, lon) + str(e) + str(f)

    def meshcode_5000(lat, lon):
        g = int(rem_lat_lv2(lat) / unit_lat_5000())*2 + int(rem_lon_lv2(lon) / unit_lon_5000()) + 1
        return meshcode_lv2(lat, lon) + str(g)

    def meshcode_2000(lat, lon):
        g = int(rem_lat_lv2(lat) / unit_lat_2000())*2
        h = int(rem_lon_lv2(lon) / unit_lon_2000())*2
        i = 5
        return meshcode_lv2(lat, lon) + str(g) + str(h) + str(i)

    def meshcode_lv3(lat, lon):
        g = int(rem_lat_lv2(lat) / unit_lat_lv3())
        h = int(rem_lon_lv2(lon) / unit_lon_lv3())
        return meshcode_lv2(lat, lon) + str(g) + str(h)

    def meshcode_lv4(lat, lon):
        i = int(rem_lat_lv3(lat) / unit_lat_lv4())*2 + int(rem_lon_lv3(lon) / unit_lon_lv4()) + 1
        return meshcode_lv3(lat, lon) + str(i)

    def meshcode_lv5(lat, lon):
        j = int(rem_lat_lv4(lat) / unit_lat_lv5())*2 + int(rem_lon_lv4(lon) / unit_lon_lv5()) + 1
        return meshcode_lv4(lat, lon) + str(j)

    def meshcode_lv6(lat, lon):
        k = int(rem_lat_lv5(lat) / unit_lat_lv6())*2 + int(rem_lon_lv5(lon) / unit_lon_lv6()) + 1
        return meshcode_lv5(lat, lon) + str(k)

    def meshcode_100(lat, lon):
        i = int(rem_lat_lv3(lat) / unit_lat_100())
        j = int(rem_lon_lv3(lon) / unit_lon_100())
        return meshcode_lv3(lat, lon) + str(i) + str(j)
    
    if level == 1:
        return meshcode_lv1(lat, lon)

    if level == 2:
        return meshcode_lv2(lat, lon)

    if level == 5000:
        return meshcode_5000(lat, lon)

    if level == 2000:
        return meshcode_2000(lat, lon)

    if level == 3:
        return meshcode_lv3(lat, lon)

    if level == 4:
        return meshcode_lv4(lat, lon)

    if level == 5:
        return meshcode_lv5(lat, lon)

    if level == 6:
        return meshcode_lv6(lat, lon)

    if level == 100:
        return meshcode_100(lat, lon)

    raise ValueError("不正な次数が指定されています。")

to_meshcode_lv1 = functools.partial(to_meshcode, level=1)
to_meshcode_lv2 = functools.partial(to_meshcode, level=2)
to_meshcode_5000 = functools.partial(to_meshcode, level=5000)
to_meshcode_2000 = functools.partial(to_meshcode, level=2000)
to_meshcode_lv3 = functools.partial(to_meshcode, level=3)
to_meshcode_lv4 = functools.partial(to_meshcode, level=4)
to_meshcode_lv5 = functools.partial(to_meshcode, level=5)
to_meshcode_lv6 = functools.partial(to_meshcode, level=6)
to_meshcode_100 = functools.partial(to_meshcode, level=100)

def to_meshpoint(meshcode, level, lat_multiplier, lon_multiplier):
    """地域メッシュコードから緯度経度を算出する。
    1次、2次、5倍メッシュ、2倍メッシュ、3次、4次、
    5次、6次、100メートルメッシュに対応している。

    Args:
        meshcode: 指定次の地域メッシュコード
        level: 地域メッシュコードの次数 
                1次:1
                2次:2
                5倍:5000
                2倍:2000
                3次:3
                4次:4
                5次:5
                6次:6
                100メートル:100
        lat_multiplier: 当該メッシュの基準点(南西端)から、緯度座標上の点の位置を当該メッシュの単位緯度の倍数で指定
        lon_multiplier: 当該メッシュの基準点(南西端)から、経度座標上の点の位置を当該メッシュの単位経度の倍数で指定
    Return:
        lat: 世界測地系の緯度(度単位)
        lon: 世界測地系の経度(度単位)

    """

    def mesh_cord(func_higher_cord, func_unit_cord, func_multiplier):
        return func_higher_cord() + func_unit_cord() * func_multiplier()

    lat_multiplier_lv = lambda: lat_multiplier
    
    lon_multiplier_lv = lambda: lon_multiplier
    
    lat_multiplier_lv1 = functools.partial(
            lambda meshcode:int(meshcode[0:2]), meshcode=meshcode)

    lon_multiplier_lv1 = functools.partial(
            lambda meshcode:int(meshcode[2:4]), meshcode=meshcode)

    lat_multiplier_lv2 = functools.partial(
            lambda meshcode:int(meshcode[4:5]), meshcode=meshcode)

    lon_multiplier_lv2 = functools.partial(
            lambda meshcode:int(meshcode[5:6]), meshcode=meshcode)

    lat_multiplier_5000 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[6:7])-1)[2:].zfill(2)[0:1]), meshcode=meshcode)

    lon_multiplier_5000 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[6:7])-1)[2:].zfill(2)[1:2]), meshcode=meshcode)

    lat_multiplier_2000 = functools.partial(
            lambda meshcode:int(meshcode[6:7])/2, meshcode=meshcode)

    lon_multiplier_2000 = functools.partial(
            lambda meshcode:int(meshcode[7:8])/2, meshcode=meshcode)

    lat_multiplier_lv3 = functools.partial(
            lambda meshcode:int(meshcode[6:7]), meshcode=meshcode)
    
    lon_multiplier_lv3 = functools.partial(
            lambda meshcode:int(meshcode[7:8]), meshcode=meshcode)
    
    lat_multiplier_lv4 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[8:9])-1)[2:].zfill(2)[0:1]), meshcode=meshcode)
    
    lon_multiplier_lv4 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[8:9])-1)[2:].zfill(2)[1:2]), meshcode=meshcode)
    
    lat_multiplier_lv5 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[9:10])-1)[2:].zfill(2)[0:1]), meshcode=meshcode)
    
    lon_multiplier_lv5 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[9:10])-1)[2:].zfill(2)[1:2]), meshcode=meshcode)
    
    lat_multiplier_lv6 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[10:11])-1)[2:].zfill(2)[0:1]), meshcode=meshcode)
    
    lon_multiplier_lv6 = functools.partial(
            lambda meshcode:int(bin(int(meshcode[10:11])-1)[2:].zfill(2)[1:2]), meshcode=meshcode)
    
    lat_multiplier_100 = functools.partial(
            lambda meshcode:int(meshcode[8:9]), meshcode=meshcode)
    
    lon_multiplier_100 = functools.partial(
            lambda meshcode:int(meshcode[9:10]), meshcode=meshcode)

    mesh_lv1_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=lambda:0, 
            func_unit_cord=unit_lat_lv1,
            func_multiplier=lat_multiplier_lv1)

    mesh_lv1_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=lambda:100, 
            func_unit_cord=unit_lon_lv1,
            func_multiplier=lon_multiplier_lv1)

    mesh_lv2_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv1_default_lat, 
            func_unit_cord=unit_lat_lv2,
            func_multiplier=lat_multiplier_lv2)

    mesh_lv2_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv1_default_lon, 
            func_unit_cord=unit_lon_lv2,
            func_multiplier=lon_multiplier_lv2)

    mesh_5000_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lat, 
            func_unit_cord=unit_lat_5000,
            func_multiplier=lat_multiplier_5000)

    mesh_5000_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lon, 
            func_unit_cord=unit_lon_5000,
            func_multiplier=lon_multiplier_5000)

    mesh_2000_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lat, 
            func_unit_cord=unit_lat_2000,
            func_multiplier=lat_multiplier_2000)

    mesh_2000_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lon, 
            func_unit_cord=unit_lon_2000,
            func_multiplier=lon_multiplier_2000)

    mesh_lv3_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lat, 
            func_unit_cord=unit_lat_lv3,
            func_multiplier=lat_multiplier_lv3)

    mesh_lv3_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lon, 
            func_unit_cord=unit_lon_lv3,
            func_multiplier=lon_multiplier_lv3)

    mesh_lv4_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lat, 
            func_unit_cord=unit_lat_lv4,
            func_multiplier=lat_multiplier_lv4)

    mesh_lv4_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lon, 
            func_unit_cord=unit_lon_lv4,
            func_multiplier=lon_multiplier_lv4)

    mesh_lv5_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv4_default_lat, 
            func_unit_cord=unit_lat_lv5,
            func_multiplier=lat_multiplier_lv5)

    mesh_lv5_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv4_default_lon, 
            func_unit_cord=unit_lon_lv5,
            func_multiplier=lon_multiplier_lv5)

    mesh_lv6_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv5_default_lat, 
            func_unit_cord=unit_lat_lv6,
            func_multiplier=lat_multiplier_lv6)

    mesh_lv6_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv5_default_lon, 
            func_unit_cord=unit_lon_lv6,
            func_multiplier=lon_multiplier_lv6)

    mesh_100_default_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lat, 
            func_unit_cord=unit_lat_100,
            func_multiplier=lat_multiplier_100)

    mesh_100_default_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lon, 
            func_unit_cord=unit_lon_100,
            func_multiplier=lon_multiplier_100)
    
    mesh_lv1_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv1_default_lat, 
            func_unit_cord=unit_lat_lv1,
            func_multiplier=lat_multiplier_lv)

    mesh_lv1_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv1_default_lon, 
            func_unit_cord=unit_lon_lv1,
            func_multiplier=lon_multiplier_lv)

    mesh_lv2_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lat, 
            func_unit_cord=unit_lat_lv2,
            func_multiplier=lat_multiplier_lv)

    mesh_lv2_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv2_default_lon, 
            func_unit_cord=unit_lon_lv2,
            func_multiplier=lon_multiplier_lv)

    mesh_5000_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_5000_default_lat, 
            func_unit_cord=unit_lat_5000,
            func_multiplier=lat_multiplier_lv)

    mesh_5000_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_5000_default_lon, 
            func_unit_cord=unit_lon_5000,
            func_multiplier=lon_multiplier_lv)

    mesh_2000_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_2000_default_lat, 
            func_unit_cord=unit_lat_2000,
            func_multiplier=lat_multiplier_lv)

    mesh_2000_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_2000_default_lon, 
            func_unit_cord=unit_lon_2000,
            func_multiplier=lon_multiplier_lv)

    mesh_lv3_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lat, 
            func_unit_cord=unit_lat_lv3,
            func_multiplier=lat_multiplier_lv)

    mesh_lv3_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv3_default_lon, 
            func_unit_cord=unit_lon_lv3,
            func_multiplier=lon_multiplier_lv)

    mesh_lv4_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv4_default_lat, 
            func_unit_cord=unit_lat_lv4,
            func_multiplier=lat_multiplier_lv)

    mesh_lv4_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv4_default_lon, 
            func_unit_cord=unit_lon_lv4,
            func_multiplier=lon_multiplier_lv)

    mesh_lv5_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv5_default_lat, 
            func_unit_cord=unit_lat_lv5,
            func_multiplier=lat_multiplier_lv)

    mesh_lv5_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv5_default_lon, 
            func_unit_cord=unit_lon_lv5,
            func_multiplier=lon_multiplier_lv)

    mesh_lv6_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv6_default_lat, 
            func_unit_cord=unit_lat_lv6,
            func_multiplier=lat_multiplier_lv)

    mesh_lv6_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_lv6_default_lon, 
            func_unit_cord=unit_lon_lv6,
            func_multiplier=lon_multiplier_lv)

    mesh_100_lat = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_100_default_lat, 
            func_unit_cord=unit_lat_100,
            func_multiplier=lat_multiplier_lv)

    mesh_100_lon = functools.partial(
            mesh_cord, 
            func_higher_cord=mesh_100_default_lon, 
            func_unit_cord=unit_lon_100,
            func_multiplier=lon_multiplier_lv)
    
    if level == 1:
        return mesh_lv1_lat(), mesh_lv1_lon()
    
    if level == 2:
        return mesh_lv2_lat(), mesh_lv2_lon()

    if level == 5000:
        return mesh_5000_lat(), mesh_5000_lon()

    if level == 2000:
        return mesh_2000_lat(), mesh_2000_lon()

    if level == 3:
        return mesh_lv3_lat(), mesh_lv3_lon()

    if level == 4:
        return mesh_lv4_lat(), mesh_lv4_lon()

    if level == 5:
        return mesh_lv5_lat(), mesh_lv5_lon()

    if level == 6:
        return mesh_lv6_lat(), mesh_lv6_lon()

    if level == 100:
        return mesh_100_lat(), mesh_100_lon()

    raise ValueError("不正な次数が指定されています。")

to_meshcentroid = functools.partial(
        to_meshpoint,
        lat_multiplier=0.5, 
        lon_multiplier=0.5)

