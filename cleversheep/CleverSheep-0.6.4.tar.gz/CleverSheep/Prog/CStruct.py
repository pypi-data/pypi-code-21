"""A new version of the Test.Struct module.

This module wraps a thin layer around the ``ctypes`` module's structure, union
and array types to provides a slightly different interface. The interface tries
to be the same as the  `CleverSheep.Test.Struct` module, which this module
effectively replaces.

This is not intended to ba any sort of replacement for ``ctypes`` just a
different way of using part of it. You may well often be better off using the
``ctypes`` module directly.

This is intended to be a replacement what for the `CleverSheep.Test.Struct`
module. The old Struct module is effectively unmaintained and this should be
considered first choice whever possible.

This depends on the availability of ``ctypes``, which is part of the C-Python
standard library from version 2.5 and available separately for Python 2.4. It
is highly recommended that you use obtain ctypes rather than use the older
``Struct`` module.

"""


import sys
from array import array
from cStringIO import StringIO

try:
    import ctypes
except ImportError: #pragma: unreachable
    raise ImportError(
 """CStruct module requires the ctypes module. For pre-Python2.5 you can
 obtain the ctypes module from http://python.net/crew/theller/ctypes/""")


_string_types = {
    ctypes.c_char: None,
}


class _Member(object):
    _seq = 0
    def __init__(self, cType):
        self.seq = _Member._seq
        self.cType = cType
        self.dims = []
        self.bits = None
        _Member._seq += 1

    def as_ctype(self, name):
        if self.dims:
            dims = list(self.dims)
            cType = self.cType

            if cType in _string_types and len(dims) > 1:
                d = dims.pop()
                class _Str(ctypes.Structure):
                    _cs_string_ = None
                    _fields_ = [("v", cType * d)]
                    def __str__(self): return self.v
                    def __getitem__(self, idx): return self.v[idx]
                    def __len__(self): return len(self.v)
                _S = _Str

                while dims:
                    class _StrArray(ctypes.Structure):
                        _cs_array_ = None
                        _fields_ = [("v", _S * dims.pop())]
                        def __setitem__(self, idx, value):
                            a = self.v[idx]
                            a.v = value
                        def __getitem__(self, idx):
                            v = self.v[idx]
                            if hasattr(v, "_cs_string_"):
                                v = v.v
                            return v
                    _S = _StrArray
                return name, _S

            while dims:
                cType = cType * dims.pop()
            return name, cType

        elif self.bits is not None:
            return name, self.cType, self.bits

        return name, self.cType

    def __getitem__(self, s):
        if isinstance(s, slice):
            assert (s.start, s.step) == (None, None)
            self.bits = s.stop
        else:
            self.dims.append(s)
        return self


_xxx = {
    'Char'             : ctypes.c_char,
    'Byte'             : ctypes.c_byte,
    'UnsignedByte'     : ctypes.c_uint8,
    'Int'              : ctypes.c_int,
    'UnsignedInt'      : ctypes.c_uint,
    'Short'            : ctypes.c_short,
    'UnsignedShort'    : ctypes.c_ushort,
    'Long'             : ctypes.c_long,
    'UnsignedLong'     : ctypes.c_ulong,
    'String'           : ctypes.c_char,
    'Float'            : ctypes.c_float,
    'Double'           : ctypes.c_double,
    'LongLong'         : ctypes.c_longlong,
    'UnsignedLongLong' : ctypes.c_ulonglong,
}


# Establish the sizes of various fundamental data types, in order to map
# them to the well defined set of C99 stdint types.
if 1:
    ctype_to_stdtint = {}
    for name in ["c_int", "c_uint"]:
        t = getattr(ctypes, name)
        l = ctypes.sizeof(t)
        if l == 4:
            ctype_to_stdtint[t] = t
        ctype_to_stdtint[t] = t

class _Type(object):
    """See the later defined Type variable for details."""
    definedTypes = {}
    def __getattr__(self, name):
        if name in _xxx:
            return _Member(_xxx.get(name))
        if name in self.definedTypes:
            return _Member(self.definedTypes.get(name))
        raise TypeError("Type.%s is not defined" % name)


#: Manages standard and user defined structured types.
#:
#: This is an instance of a hidden anonymous type. It has no pure
#: attributes, but appears to have attributes with the same name as
#: standard or defined types. For example::
#:
#:     Type.Int          # A standard type
#:     Type.MyStruct     # A defined type.
#:
#: See the user guide in the module docs for how Type gets used.
Type = _Type()

class Format(object):
    """The different possible formats."""
    Native          = "@"       # Native format, native size
    LittleEndian    = "<"       # Standard size
    BigEndian       = ">"       # Standard size
    Network         = "!"       # Network byte order


class MetaCompoundType(type):
    def __new__(cls, name, bases, d, cType):
        if name in ("Struct", "Union"):
            return type.__new__(cls, name, bases, d)

        if name in _xxx:
            raise TypeError("Attempt to redefine basic CStruct type %s" % (
                name))

        # Get each Element field, sorted by id.
        byteOrder = d.pop("_byteOrder", Format.Native)
        elems = sorted(
            ((k, v) for (k, v) in d.iteritems() if isinstance(v, _Member)),
            key=lambda x:x[1].seq)

        dd = dict((n, v) for n, v in d.iteritems()
                            if not isinstance(v, _Member))
        dd["_fields_"] = [(m.as_ctype(k)) for k, m in elems]
        dd["__init__"] = Struct__init__
        dd["__setattr__"] = Struct__setattr__
        dd["_meta"] = property(_meta)
        kk = _ctypeMap[(cType, byteOrder)]
        klass = type(name, (kk,), dd)
        _Type.definedTypes[name] = klass
        klass._cmeta = CMeta(klass)
        return klass

    def __init__(cls, name, bases, d):
        super(MetaCompoundType, cls).__init__(name, bases, d)


_ctypeMap = {
    ("struct", Format.Native): ctypes.Structure,
    ("struct", Format.BigEndian): ctypes.BigEndianStructure,
    ("struct", Format.LittleEndian): ctypes.LittleEndianStructure,
    ("union", Format.Native): ctypes.Union,
    ("union", Format.BigEndian): ctypes.Union,
    ("union", Format.LittleEndian): ctypes.Union,
}

class MetaStructType(MetaCompoundType):
    def __new__(cls, name, bases, d):
        klass = super(MetaStructType, cls).__new__(cls, name, bases, d,
                "struct")
        # klass._meta.compTypeName = "struct"
        return klass


class MetaUnionType(MetaCompoundType):
    def __new__(cls, name, bases, d):
        klass = super(MetaUnionType, cls).__new__(cls, name, bases, d,
                "union")
        # klass._meta.compTypeName = "struct"
        return klass


class Struct(object):
    """The base class used to define the equivalent of C structs.

    The user guide in this module's documentation provides useful examples,
    but basically to define a Python class to map to a C-struct you do
    something like::

        # Python like this                      # is equivalent to C like this
        class Message(Struct):                  # struct Message {
            len   = Type.UnsignedInt[:24]       #    unsigned int len:24;
            type  = Type.UnsignedInt[:8]        #    unsigned int type:8;
            body  = Type.MsgBody                #    union MsgBody body;
                                                # };

    The `Union` class provides an example of what the ``body`` might look like.
    """
    __metaclass__ = MetaStructType


class Union(object):
    __metaclass__ = MetaUnionType


def Struct__init__(self, _rawData=None, trim=False, **kwargs):
    if _rawData is not None:
        self._meta.setBytes(_rawData)
    for name, value in kwargs.iteritems():
        setattr(self, name, value)


# TODO: This only exist to raise AttributeError when we try to assign
#       to a non-existant attribute. For some reason, ctypes lets us do
#       jsut that without any error.
def Struct__setattr__(self, name, value):
    if not hasattr(self, name):
        raise AttributeError(name)
    ctypes.Structure.__setattr__(self, name, value)


class Meta(object):
    def __init__(self, o):
        self.o = o

    def setBytes(self, rawData, trim=False):
        # Complain if the rawData is too large.
        lRawData = len(rawData)
        if lRawData > self.size:
            raise ValueError("Tried to assign %d bytes to a %d byte struct" %
                    (lRawData, self.size))

        # If trimming then zero the destination first.
        o = self.o
        if trim:
            ctypes.memset(ctypes.pointer(o), 0, self.size)

        # Convert a list or tuple to a string.
        if isinstance(rawData, (list, tuple)):
            s = array('B', rawData).tostring()
        else:
            # Convert an array (or duck typed equivalent) to a string.
            try:
                s = rawData.tostring()
            except AttributeError:
                s = rawData

        # Copy into the struct.
        ctypes.memmove(ctypes.pointer(o), ctypes.c_char_p(s), len(s))

    @property
    def size(self):
        return ctypes.sizeof(self.o)

    @property
    def s(self):
        o = self.o
        return ctypes.string_at(ctypes.addressof(o), ctypes.sizeof(o))

    @property
    def bytes(self):
        return array("B", self.s)

    @property
    def hex(self):
        return ["%02x" % v for v in self.bytes]

    @property
    def children(self):
        o = self.o
        return [(name, getattr(o, name)) for name, t in o._fields_]

    @property
    def name(self):
        return self.o.__class__.__name__

    def addr(self):
        return ctypes.addressof(self.o)

    def _dumpUnion(self, info, o, uName, actualOff=None):
        info.f.write(u"\n")
        info = info.copy()
        mChoice = None
        if not info.describeOnly:
            selectors = info.selectors
            if selectors:
                selector = selectors.get(uName, None)
                if selector:
                    mChoice = selector(info.parent)
        if mChoice is None:
            info.describeOnly = True

        for data in o._fields_:
            stop = True
            try:
                mName, mType, mBits = data
            except ValueError:
                (mName, mType), mBits = data, None
            mDesc = getattr(o.__class__, mName)
            mInst = getattr(o, mName)
            mLength = getattr(mType, "_length_", None)
            mOffset = getattr(mDesc, "offset", "")
            if mChoice is not None:
                if mChoice == mName:
                    stop = False
                else:
                    continue
            if actualOff:
                info.mOffset = actualOff
            if mBits:
                width, start = mDesc.size >> 16, mDesc.size & 0xFFFF
                mBits = (start, width)
                mSize = None

            self._dumpInst(info.indent(stop=stop),
                    mInst, mName, mType, mBits=mBits, actualOff=actualOff)

    def _dumpStructure(self, info, o):
        info.f.write(u"\n")
        base = info.copy()
        selectors = getattr(o, "_selectors_", None)
        for data in o._fields_:
            try:
                mName, mType, mBits = data
            except ValueError:
                (mName, mType), mBits = data, None
            mDesc = getattr(o.__class__, mName)
            mInst = getattr(o, mName)
            mLength = getattr(mType, "_length_", None)
            mOffset = getattr(mDesc, "offset", "")
            if mOffset > 0:
                info.mOffset = base.mOffset + mOffset
            if mBits:
                width, start = mDesc.size >> 16, mDesc.size & 0xFFFF
                mBits = (start, width)
                mSize = None

            self._dumpInst(info.indent(selectors=selectors, parent=o),
                    mInst, mName, mType, mBits=mBits)

    def _getStrArrayDims(self, o):
        dims = []
        x = o
        while hasattr(x, "_cs_array_"):
            dims.append(x.v._length_)
            x = x.v[0]
        dims.append(ctypes.sizeof(x))
        return dims

    def _dumpStrArray(self, info, o):
        info.f.write(u"\n")
        self._dumpStrArrayElements(info.indent(), o.v)

    def _dumpStrArrayElements(self, info,o):
        f, ind = info.f, info.ind
        baseOff = info.mOffset
        step = ctypes.sizeof(o) // getattr(o.__class__, "_length_")
        for i, el in enumerate(o):
            off = baseOff + i * step
            f.write(u"%-5s: %s[%s] %r\n" % (off, ind, i, el.v))

    def _getDims(self, o):
        x, dims = o, []
        while hasattr(x, "_length_"):
            dims.append(x._length_)
            x = x[0]
        return dims

    def _getArrayType(self, o):
        x = o
        t = o._type_
        while hasattr(x, "_length_"):
            t = x._type_
            x = x[0]
        return t.__name__

    def _dumpArray(self, info, o, dims):
        info.f.write(u"\n")
        if info.describeOnly:
            el = o
            for x in dims:
                el = el[0]
            self._dumpInst(info.indent(), el)
        else:
            self._dumpElements(info.indent(), o)

    def _dumpElements(self, info, o):
        f, ind = info.f, info.ind
        baseOff = info.mOffset
        step = ctypes.sizeof(o) // getattr(o.__class__, "_length_")

        for i, el in enumerate(o):
            off = baseOff + i * step
            if hasattr(el, "_length_"):
                f.write(u"%-5s: %s[%d]\n" % (off, ind, i,))
                self._dumpElements(info.indent(mOffset=off), el)
            else:
                f.write(u"%-5s: %s[%d]" % (off, ind, i))
                self._dumpInst(info, el, noType=1, actualOff=off)

    def _getPart1(self, o, mType):
        if mType is None:
            mType = o.__class__
        mTypeName = mType.__name__
        if hasattr(o, "_cs_array_"):
            dims = self._getStrArrayDims(o)
            return "c_char", "SA", dims
        if isinstance(o, ctypes.Structure):
            return "struct %s" % mTypeName, "S", []
        if isinstance(o, ctypes.Union):
            return "union %s" % mTypeName, "U", []

        mLength = getattr(o, "_length_", None)
        tLength = getattr(mType, "_length_", None)
        if tLength is not None:
            if mLength is not None:
                dims = self._getDims(o)
                mTypeName = self._getArrayType(o)
                if isinstance(o[0], ctypes.Structure):
                    mTypeName = "struct %s" % mTypeName
                elif isinstance(o[0], ctypes.Union):
                    mTypeName = "union %s" % mTypeName
                return mTypeName, "A", dims
            else:
                mTypeName = mType._type_.__name__
                dims = [tLength]
                return mTypeName, "O", dims

        return mTypeName, "O", []

    def _dumpInst(self, info, o, mName=None, mType=None, noType=False,
            mBits=None, actualOff=None):
        # Work out type name form and type code.
        f, ind = info.f, info.ind

        a, t, dims = self._getPart1(o, mType)
        if not noType:
            if dims:
                a = u"%s%s" % (a, dims)
            if mBits is not None:
                a = u"%s;%d:%d" % (a, mBits[0], mBits[1])

            if mName is not None:
                f.write(u"%-5s: %s%-20s %s" % (info.mOffset, ind, a, mName))
            else:
                f.write(u"%-5s: %s%s" % (info.mOffset, ind, a))

        if info.stop:
            f.write(u"\n")
            return

        if t == "S":
            return self._dumpStructure(info, o)
        if t == "U":
            return self._dumpUnion(info, o, mName, actualOff=actualOff)
        if t == "A":
            return self._dumpArray(info, o, dims)
        if t == "SA":
            return self._dumpStrArray(info, o)

        if not info.describeOnly:
            f.write(u" = %r\n" % o)
        else:
            f.write(u"\n")

    def dump(self, describeOnly=False):
        f = StringIO()
        info = _Info(f=f, ind="", describeOnly=describeOnly, mOffset=0,
                stop=False, selectors=None, parent=None)
        self._dumpInst(info, self.o)
        return f.getvalue()

    def describe(self):
        return self.dump(describeOnly=True)


class _Info(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def copy(self, **kwargs):
        n = _Info(**self.__dict__)
        n.__dict__.update(kwargs)
        return n

    def indent(self, **kwargs):
        return self.copy(ind=self.ind + "  ", **kwargs)


class CMeta(object):
    def __init__(self, c):
        self.c = c

    # TODO:See if this can be done without allocating an object.
    @property
    def size(self):
        o = self.c()
        return o._meta.size

    def describe(self):
        o = self.c()
        return o._meta.describe()


def _meta(self):
    return Meta(self)


if __name__ == "__main__": #pragma: debug
    class A(Struct):
        aa = Type.Int[3][2]
        bb = Type.String[2][5]
        ss = Type.String[5]

    class S(Struct):
        a = Type.Int
        b = Type.A[2]

    s = S()
    print(s._meta.dump())
