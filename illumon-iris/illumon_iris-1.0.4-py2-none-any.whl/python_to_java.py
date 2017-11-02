#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#


import sys
import time
import pandas as pd
import jpy
from .constants import *

# python type string -> (java type string, java null, encoding function)
python_type_map = {}

def encode_bool(col):
    a = jpy.array("bool", col.size)

    for i in range(col.size):
        a[i] = col[i]

    return a

def encode_basic(col, jtype):
    a = jpy.array(jtype, col.size)

    for i in range(col.size):
        a[i] = col[i]

    return a

def encode_datetime64(col, jtype):
    assert jtype == 'com.illumon.iris.db.tables.utils.DBDateTime'
    DBDateTime = jpy.get_type('com.illumon.iris.db.tables.utils.DBDateTime')
    a = jpy.array("com.illumon.iris.db.tables.utils.DBDateTime", col.size)

    if sys.version_info[0] > 2:
        cst = int
    else:
        cst = long

    for i in range(col.size):
        v = col[i]
        if v == None or pd.isnull(v):
            a[i] = None
        else:
            ns = cst(time.mktime(v.timetuple()))*1000000000 + v.microsecond*1000 + v.nanosecond
            t = DBDateTime(ns)
            a[i] = t

    return a

def encode_object_typed(col, typ):
    jtyp, jnull, encoder = python_type_map[typ]

    a = jpy.array(jtyp, col.size)

    for i in range(col.size):
        v = col[i]
        if v == None or pd.isnull(v):
            a[i] = jnull
        else:
            a[i] = v

    return a


def encode_object(col, jtype):
    #are there any reasonable uses or checks on jtype that should happen here?

    types = set()

    for i in range(col.size):
        typ = type(col[i])
        typ_name = typ.__name__
        typ_module = typ.__module__

        if typ_module == "__builtin__" or typ_module == "builtins":
            name = typ_name
        else:
            name = typ_module + "." + typ_name

        types.add( name )

    types.discard("NoneType")

    if len(types) == 1:
        return encode_object_typed(col, types.pop())
    else:
        return encode_object_typed(col, "object")


# Booleans
python_type_map["bool"] = ("java.lang.Boolean",None,encode_basic)
python_type_map["bool_"] = python_type_map["bool"]
python_type_map["bool8"] = python_type_map["bool"]

# Floating-point numbers:
python_type_map["float32"] = ("float", NULL_FLOAT, encode_basic)
python_type_map["float64"] = ("double", NULL_DOUBLE, encode_basic)
python_type_map["float16"] = python_type_map["float32"]
python_type_map["half"] = python_type_map["float32"]
python_type_map["single"] = python_type_map["float32"]
python_type_map["double"] = python_type_map["float64"]
python_type_map["float_"] = python_type_map["float64"]
# python_type_map["longfloat"] = # longfloat	compatible: C long float	'g'
# python_type_map["float96"] = # float96	96 bits, platform?
# python_type_map["float128"] = # float128	128 bits, platform?

# Integers:
python_type_map["int8"] = ("byte", NULL_BYTE, encode_basic)
python_type_map["int16"] = ("short", NULL_SHORT, encode_basic)
python_type_map["int32"] = ("int", NULL_INT, encode_basic)
python_type_map["int64"] = ("long", NULL_LONG, encode_basic)
python_type_map["byte"] = python_type_map["int8"]
python_type_map["short"] = python_type_map["int16"]
python_type_map["intc"] = python_type_map["int32"]
python_type_map["int"] = python_type_map["int64"]
python_type_map["int_"] = python_type_map["int64"]
python_type_map["long"] = python_type_map["int64"]  # python longs may do infinite size
python_type_map["longlong"] = python_type_map["int64"]
# python_type_map["intp"] = # intp	large enough to fit a pointer	'p'

# Unsigned integers:
python_type_map["uint8"] = python_type_map["int16"]
python_type_map["uint16"] = python_type_map["int32"]
python_type_map["uint32"] = python_type_map["int64"]
python_type_map["ubyte"] = python_type_map["int16"]
python_type_map["ushort"] = python_type_map["int32"]
python_type_map["uintc"] = python_type_map["int64"]
python_type_map["uint"] = python_type_map["int64"]
# python_type_map["ulonglong"] = # ulonglong	compatible: C long long	'Q'
# python_type_map["uintp"] = # uintp	large enough to fit a pointer	'P'
# python_type_map["uint64"] = # uint64	64 bits

# Complex floating-point numbers:
# python_type_map["csingle"] = # csingle	 	'F'
# python_type_map["complex_"] = # complex_	compatible: Python complex	'D'
# python_type_map["clongfloat"] = # clongfloat	 	'G'
# python_type_map["complex64"] = # complex64	two 32-bit floats
# python_type_map["complex128"] = # complex128	two 64-bit floats
# python_type_map["complex192"] = # complex192	two 96-bit floats, platform?
# python_type_map["complex256"] = # complex256	two 128-bit floats, platform?

# Objects:
python_type_map["str"] = ("java.lang.String",None,encode_basic)
python_type_map["str_"] = python_type_map["str"]
python_type_map["unicode"] = python_type_map["str"]
python_type_map["unicode_"] = python_type_map["str"]
# python_type_map["void"] = # void	 	'V#'
python_type_map["object"] = ("java.lang.Object",None,encode_object)
python_type_map["object_"] = python_type_map["object"]
python_type_map["java.util.Date"] = python_type_map["object"]
python_type_map["numpy.datetime64"] = ("com.illumon.iris.db.tables.utils.DBDateTime", None, encode_datetime64)
python_type_map["datetime64[ns]"] = ("com.illumon.iris.db.tables.utils.DBDateTime", None, encode_datetime64)
