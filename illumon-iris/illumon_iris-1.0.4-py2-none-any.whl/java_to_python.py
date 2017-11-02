#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#

import sys
import datetime
import numpy as np
import jpy
from .constants import *

# java type string -> parse function
java_type_map = {}


def parse_char(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.object)

    if sys.version_info[0] < 3:
        f = unichr
    else:
        f = chr

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getChar(k)
        a[i] = None if v==NULL_CHAR else f(v)

    return a

def parse_float(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.float32)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getFloat(k)
        a[i] = np.nan if v==NULL_FLOAT else v

    return a

def parse_double(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.float64)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getDouble(k)
        a[i] = np.nan if v==NULL_DOUBLE else v

    return a

def parse_short(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.float32)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getShort(k)
        a[i] = np.nan if v==NULL_SHORT else v

    return a

def parse_int(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.float64)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getInt(k)
        a[i] = np.nan if v==NULL_INT else v

    return a

def parse_long(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.object)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getLong(k)
        a[i] = None if v==NULL_LONG else v

    return a

def parse_byte(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.float16)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getByte(k)
        a[i] = np.nan if v==NULL_BYTE else v

    return a

def parse_boolean(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.object)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.getBoolean(k)
        a[i] = v

    return a

def parse_datetime(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.object)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        v = column_source.get(k)
        if v==None:
            a[i] = None
        else:
            us = v.getNanos()
            s = us * 1e-9
            ts = datetime.datetime.fromtimestamp(s)
            a[i] = ts

    return a

def parse_object(index, column_source, iterator_type):
    sz = index.size()
    a = np.zeros(sz,dtype=np.object)

    index_iter = index.iterator()
    
    index_iter = jpy.cast(index_iter, iterator_type)
    for i in range(sz):
        k = index_iter.nextLong()
        a[i] = column_source.get(k)

    return a

java_type_map['char'] = parse_char
java_type_map['float']  = parse_float
java_type_map['double'] = parse_double
java_type_map['short'] = parse_short
java_type_map['int'] = parse_int
java_type_map['long'] = parse_long
java_type_map['byte'] = parse_byte
java_type_map['class java.lang.Boolean'] = parse_boolean
java_type_map['class com.illumon.iris.db.tables.utils.DBDateTime'] = parse_datetime
java_type_map['object'] = parse_object
