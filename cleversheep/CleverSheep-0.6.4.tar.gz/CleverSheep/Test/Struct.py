#!/usr/bin/env python
"""High level support for C structures and unions.

Introduction

This module provides support for creating Python classes, which closely map to
C structures and unions.

The module uses some meta-class programming tricks and (quite frankly) abuse of
Python syntax in order to make the mapping from Python classes to the
corresponding C reasonably obvious to the human reader.


Credits

This is inspired by an *ASPN recipe* by *Brian McErlean* and some snippets of
his code probably remain here.
"""


import sys
from array import array
import struct
from cStringIO import StringIO

_name_to_code = {
    'Char'             : 'c',
    'Byte'             : 'b',
    'UnsignedByte'     : 'B',
    'Int'              : 'i',
    'UnsignedInt'      : 'I',
    'Short'            : 'h',
    'UnsignedShort'    : 'H',
    'Long'             : 'l',
    'UnsignedLong'     : 'L',
    'String'           : 's',
    'Float'            : 'f',
    'Double'           : 'd',
    'LongLong'         : 'q',
    'UnsignedLongLong' : 'Q',
    }

_code_to_name = {}
for n in _name_to_code:
    _code_to_name[_name_to_code[n]] = n
del n

__all__ = ["Type", "Struct", "Union", "Format", "ProxyCompound", "ProxyArray"]


def _zeros(count):
    """Generator: Yields ``count`` zeros."""
    while count:
        yield 0
        count -= 1


def _makeBytes(countOrSource):
    """Creates a byte array of ``count`` zeros."""
    try:
        if int(countOrSource) == countOrSource:
            return array('B', _zeros(countOrSource))
    except ValueError:
        pass

    rawData = countOrSource
    if isinstance(rawData, (str, )):
        rawData = array('B', rawData.encode("ascii"))
    elif isinstance(rawData, (list, tuple)):
        rawData = array('B', rawData)
    return array('B', rawData)


class Format(object):
    """The different possible formats."""
    Native          = "@"       # Native format, native size
    LittleEndian    = "<"       # Standard size
    BigEndian       = ">"       # Standard size
    Network         = "!"       # Network byte order


class MetaInfo(object):
    """The base class for a collection of meta-info classes.

    The `Struct` and `Union` classes are designed to create derived classes
    that mirror C structures. Instances of these plus
    other helper classes provide a ``_meta`` member, which provides and manages
    information about the object. The leading underscore is to prevent naming
    clashes with actual C member variable names.

    :Ivar size:
        The nominal size of the structure, which is the number of bytes that
        a complete structure will contain. This is not necessarily the number
        of bytes that the it actually contains because a `Struct` can be mapped
        to fewer bytes, which is given by `dataSize`.
    """
    def __init__(self, obj, bytes=None):
        self.obj = obj      #: The class/object to which this relates.
        if bytes == None:
            self.bytes = array('B', [])
        else:
            self.bytes = bytes  #: The bytes for this class/object.

    @property
    def children(self):
        obj = self.obj
        cls = obj.__class__
        info = []
        for name in obj._meta.ct_info:
            idx, memberType, offset = obj._meta.ct_info[name]
            info.append((idx, name, memberType, offset))
            info.sort()
        children = []
        for idx, name, memberType, offset in info:
            v = getattr(obj, name)
            children.append((name, v))
        return children

    @property
    def s(self):
        return self.bytes[:self.size].tostring()

    @property
    def hex(self):
        return ["%02x" %v for v in self.bytes[:self.size]]

    @property
    def dataSize(self):
        """The number of bytes mapped to this struct.

        This may be less than ``_meta,size`` since the struct may be mapped to
        a byte array that is shorter that the struct's nominal size.

        """
        return len(self.bytes[:self.size])

    @property
    def name(self):
        return self.obj.__class__.__name__

    def _describeObject(self, cls, stream, ind=0, baseOffset=0):
        pad = "  " * ind
        if ind == 0:
            stream.write("%s %s" % (cls._meta.compTypeName, cls.__name__))
            stream.write("\n")
        info = []
        for name in cls._meta.ct_info:
            idx, memberType, offset = cls._meta.ct_info[name]
            info.append((idx, name, memberType, offset))
            info.sort()
        for idx, name, memberType, offset in info:
            lWidth = 40 - len(pad)
            stream.write("  %s%-*s : %s, offset=%d\n" % (
                    pad, lWidth, name, memberType._meta.typeName(),
                    baseOffset + offset))
            if isinstance(memberType, CompoundMember):
                memberType.struct._meta.describe(ind + 1,
                        baseOffset=baseOffset+offset, stream=stream)
            if isinstance(memberType, ArrayMember):
                memberType._meta.describe(ind + 1,
                        baseOffset=baseOffset+offset, stream=stream)

    def _dumpObject(self, obj, f=sys.stdout, ind=0):
        cls = obj.__class__
        pad = "  " * ind
        if ind == 0:
            try:
                f.write("%s %s\n" % (cls._meta.compTypeName, cls.__name__))
            except AttributeError: #pragma: unreachable - TODO: Is this True?
                # This is not the root of a struct.
                pass
        info = []
        for name in obj._meta.ct_info:
            idx, memberType, offset = obj._meta.ct_info[name]
            info.append((idx, name, memberType, offset))
            info.sort()
        for idx, name, memberType, offset in info:
            v = getattr(obj, name)
            hv = hexVal(v)
            if hv: hv = "/ " + hv
            if isinstance(memberType, (CompoundMember)):
                t = memberType._meta.typeName()
                f.write("  %s%s : %s\n" % (pad, name, memberType._meta.typeName()))
                v._meta.dump(stream=f, ind=ind+1)

            elif isinstance(memberType, ArrayMember):
                f.write("  %s%s : Array[%d]\n" % (pad, name,
                        memberType._meta.dimension))
                v._meta._dumpObject(v, f=f, ind=ind+1)

            else:
                if memberType._formatChars.endswith("s"):
                    v = v.encode("ascii")
                f.write("  %s%s = %r%s\n" % (pad, name, v, hv))

    def _findObject(self, obj, nameToFind, data):
        info = []
        if isinstance(obj, ProxyArray):
            return None
        for name in obj._meta.ct_info:
            idx, memberType, offset = obj._meta.ct_info[name]
            info.append((idx, name, memberType, offset))
            info.sort()

        for idx, name, memberType, offset in info:
            v = getattr(obj, name)
            if name == nameToFind:
                data.append(v)

            if isinstance(memberType, (CompoundMember)):
                t = memberType._meta.typeName()
                v._meta.find(nameToFind, data)

            elif isinstance(memberType, ArrayMember):
                xx = v._meta._findObject(v, nameToFind, data)
                if xx is not None: #pragma: to test
                    data.append(xx)


def hexVal(v):
    """Try to convert a value to hex."""
    if isinstance(v, (int, long)):
        return hex(v)
    if isinstance(v, basestring) and len(v) == 1:
        return hex(ord(v))
    return ""


class CompoundMetaInfoBase(MetaInfo):
    def typeName(self):
        try:
            return "%s %s" % (self.compTypeName, self.obj.__name__)
        except AttributeError: #pragma: to test
            return "%s %s" % (self.compTypeName, self.obj.__class__.__name__)


class InstanceMetaInfo(CompoundMetaInfoBase):
    def setBytes(self, rawData, trim=False):
        """Set the structs data from a raw byte sequence.

        This allows the stucture's array of bytes to be set directly from a
        string, list, tuple or array. If supplied raw data is smaller than the
        struct then bytes at the end are unchanged.

        :Param rawData:
            This should either be a string, a list/tuple of byte values or an
            ``array`` instance of type 'B', see the standard *array* module.
        :Param trim:
            If True then the structures byte array is trimmed down to the
            size of the raw data.
        """
        # Verify that the structure supports this many bytes.
        lRawData = len(rawData)
        if lRawData > self.size:
            raise ValueError("Tried to assign %d bytes to a %d byte struct" %
                    (lRawData, self.size))

        if trim:
            self.bytes = _makeBytes(rawData)
        else:
            # Extend the underlying byte array if it is not already large enough.
            lBytes = len(self.bytes)
            if lRawData > lBytes:
                self.bytes.extend(_makeBytes(lRawData - lBytes))

            # Over-write the current bytes with the new raw data.
            if isinstance(rawData, (str, )):
                rawData = array('B', rawData.encode("ascii"))
            elif isinstance(rawData, (list, tuple)):
                rawData = array('B', rawData)
            elif not isinstance(rawData, (array,)):
                rawData = array('B', rawData)
            self.bytes[0:lRawData] = rawData

    def describe(self, ind=0, baseOffset=0, stream=None):
        s, stream = stream, stream or StringIO()
        self._describeObject(self.obj.__class__, stream, ind,
                baseOffset=baseOffset)
        if s is None:
            return stream.getvalue()

    def dump(self, stream=None, ind=0):
        s, stream = stream, stream or StringIO()
        self._dumpObject(self.obj, f=stream, ind=ind)
        if s is None:
            return stream.getvalue()

    def find(self, name, data=None):
        if self.obj is None:
            return None
        if data is None:
            data = []
        self._findObject(self.obj, name, data)
        return data

    def addr(self):
        addr, l = self.bytes.buffer_info()
        return addr

    def __getattr__(self, name):
        if hasattr(self.obj.__class__, "_meta"):
            return getattr(self.obj.__class__._meta, name)
        raise AttributeError("%r object has no attribute %r" % (
                self.__class__.__name__, name), name)


class ClassMetaInfo(CompoundMetaInfoBase):
    def describe(self, ind=0, baseOffset=0, stream=None):
        s, stream = stream, stream or StringIO()
        self._describeObject(self.obj, stream, ind, baseOffset=baseOffset)
        if s is None:
            return stream.getvalue()

    def find(self, name, data=None): #pragma: to test
        if self.obj is None:
            return None
        if data is None:
            data = []
        self._findObject(self.obj, name, data)
        return data


class MemberMetaInfo(MetaInfo):
    def typeName(self):
        name = _code_to_name[self.obj._formatChars[-1]]
        if self.obj._isBitField:
            name += ":" + str(self.obj._bits)
        return name


class ArrayMeta(MetaInfo):
    def describe(self, ind=0, baseOffset=0, stream=None):
        s, stream = stream, stream or StringIO()
        memberType = self.obj._meta.elementType
        if isinstance(memberType, CompoundMember):
            memberType.struct._meta.describe(ind + 1, baseOffset=baseOffset,
                    stream=stream)
        if s is None: #pragma: to test
            return stream.getvalue()

    def typeName(self):
        n = self.obj._meta.elementType._meta.typeName()
        return "%s[%d]" % (n, self.obj._meta.dimension)

    def calcArrayByteOffest(self, idxParam):
        idx = idxParam
        if idx < 0:
            idx += self.dimension
        if not 0 <= idx < self.dimension:
            raise IndexError(idxParam)

        offset = self.offset
        offset += self.elementSize * idx
        return offset

    def _dumpObject(self, obj, f=sys.stdout, ind=0):
        pad = "  " * ind
        for i in range(0, min(5, self.dimension)):
            f.write("%s[%d]" % (pad, i))
            v = obj[i]
            if isinstance(self.elementType, (CompoundMember)):
                t = self.elementType._meta.typeName()
                f.write(" : %s\n" % (self.elementType._meta.typeName()))
                v._meta.dump(stream=f, ind=ind+1)

            elif isinstance(self.elementType, ArrayMember): #pragma: to test
                f.write(" : Array[%d]\n" % (self.elementType._meta.dimension))
                v._meta._dumpObject(v, f=f, ind=ind+1)

            else:
                f.write(" = %r\n" % (v,))


class CompoundMetaInfo(MetaInfo):
    def typeName(self):
        return self.obj.struct._meta.typeName()


class _Int(int):
    def __new__(cls, v):
        klass = super(_Int, cls).__new__(cls, v)
        klass._meta = InstanceMetaInfo(None, None)
        return klass


class _Long(long):
    def __new__(cls, v):
        klass = super(_Long, cls).__new__(cls, v)
        klass._meta = InstanceMetaInfo(None, None)
        return klass


def calcAlignment(size):
    alignment = size
    if alignment == 3: #pragma: to test
        alignment = 4
    elif alignment > 4:
        alignment = 4
    return alignment


class Member(object):
    """Holds the details of a C struct/union member.

    When a `Struct`/`Union` is defined, as in::

        S = XXX(Struct):
            a = Type.Int
            b = Type.AnotherStruct
            ...

    then each ``a = Type....`` causes a new Member instance to be created;
    so ``a`` is a Member instance and ``b`` is ``Member`` instance. In this
    example ``a``, ``b``, etc represent members of the C `Struct`/`Union`
    that is being represented.

    :Ivar _meta:
        The `MemberMetaInfo` data for this member.
        TODO: Why member meta info?

    :Ivar uid:
        A unique identifier. This is an integer value, assigned at
        construction. Each new `Member` instance get the next highest id, and
        this is used to sort `Struct`/`Union` members into 'declaration' order,
        which is (of course) vital for correct mapping the the C-type being
        represented.

    :Ivar structFmtChars:
        If not an empty string, this is the format char (or chars) that define
        this member; see the standard ``struct`` module for details.

    :Ivar _size:
        The number of bytes required to store this member.

    :Ivar alignment:
        How this member need to be aligned. It can have the values 1 (8-bit
        aligned), 2 (16-bit aligned), 4 (32-bit aligned). In the future a value
        of 8 may be required/supported.

    :Ivar _bits, _spare_bits, _bit_src, _start_bit, _isBitField:
        Used for bit-fields and currently considered experimental.

    """
    _uid = 0
    metaInfo = MemberMetaInfo
    def __init__(self, structFmtChars="", size=1, pad=1):
        self.uid = Member._uid
        Member._uid += 1

        self._meta = self.metaInfo(self, None)
        self._meta.byteOrder = None

        # Work out the size and alignment.
        if structFmtChars:
            self._size = struct.calcsize(structFmtChars)
            self.alignment = calcAlignment(self._size)
        else:
            self._size = size
            self.alignment = 1
            # TODO: What about arrays?

        assert self.alignment in (1, 2, 4)
        self._formatChars = structFmtChars  # TODO: This could be improved

        # Bit field support
        self._bit_width = self._spare_bits = self._size * 8
        self._start_bit = 0

        self._bits = self._bit_width
        self._bit_src = self
        self._isBitField = False

    def setDefByteOrder(self, byteOrder):
        if self._meta.byteOrder is None:
            self._meta.byteOrder = byteOrder

    def unpack(self, s, mask=True):
        assert self.__class__ is Member
        v = struct.unpack(self._meta.byteOrder + self._formatChars, s)[0]
        if not self._isBitField or not mask:
            if self._formatChars.endswith("s"):
                return v.decode("ascii").split("\0")[0]
            if isinstance(v, int):
                v = _Int(v)
                v._meta.size = self._size
            elif isinstance(v, long):
                v = _Long(v)
                v._meta.size = self._size
            return v

        m1 = _masks[self._bits-1];
        v = (v >> self._start_bit) & m1
        return v

    def pack(self, v):
        assert self.__class__ is Member
        return struct.pack(self._meta.byteOrder + self._formatChars, v)

    def __len__(self): return self._size

    def __getitem__(self, s):
        if isinstance(s, slice):
            assert (s.start, s.step) == (None, None)
            return self._asBitField(s.stop)

        # Treat string as a special case, since any dimension does make it an
        # array.
        if self._formatChars == "s":
            self._size = s
            self._formatChars = "%ds" % s
            return self
        elif self._formatChars.endswith("s"):
            # Aha!, we actually want an array of strings.
            self._formatChars = "%ds" % s
            s, self._size = self._size, s
            return self._asArray(s)

        return self._asArray(s)


    def _asArray(self, dimension):
        xxx = []
        q = self
        while isinstance(q, ArrayMember):
            xxx.append(q._meta.dimension)
            q = q._meta.elementType

        arr = ArrayMember(q, dimension)
        if xxx:
            xxx.reverse()
            for dim in xxx:
                arr = ArrayMember(arr, dim)
        return arr

    def _asBitField(self, bitCount):
        self._isBitField = True
        self._bits = bitCount
        return self

    def hasRoom(self, m):
        assert self._bits is not None
        if self._formatChars != m._formatChars:
            return False
        # print("ROOM", self._spare_bits, m._bits)
        if self._spare_bits < m._bits:
            return False

        m._bit_src = self
        m._size = 0
        # m._size = 0
        # print("OLD_ST",  m._start_bit, self._size)
        # m._start_bit = self._size * 8 - self._spare_bits
        # m._start_bit = self._spare_bits - self._size * 8 - self._spare_bits
        # m._start_bit = self._spare_bits - m._bits
        # print("NEW ST", m._start_bit, self._spare_bits)
        # self._spare_bits -= m._bits
        return True

    def makeFld(self, other):
        other._start_bit = self._bit_width - self._spare_bits
        self._spare_bits -= other._bits
        # print("ADD", self._bits, "leaving", self._spare_bits, "field starts at", self._start_bit)



class ArrayMember(Member):
    metaInfo = ArrayMeta
    def __init__(self, elementType, dimension):
        l = elementType._size * dimension
        # s = elementType._formatChars * 2
        # elementSize = struct.calcsize(s) - elementType._size
        # fmt = "%ds" % (elementSize * dimension)
        assert elementType.alignment in (1, 2, 4)
        Member.__init__(self, size=l, pad=elementType.alignment)
        self._meta.dimension = dimension
        self._meta.elementType = elementType
        self._meta.elementSize = elementType._size
        self._meta.size = elementType._size * dimension
        # self._meta.name = elementType._meta._name

    def setDefByteOrder(self, byteOrder):
        self._meta.elementType.setDefByteOrder(byteOrder)


class CompoundMember(Member):
    metaInfo = CompoundMetaInfo
    def __init__(self, structure):
        Member.__init__(self, size=structure._meta.size,
                pad=structure._meta.ct_alignment)
        self.struct = structure
        self.alignment = structure._meta.ct_alignment

    def setDefByteOrder(self, byteOrder):
        pass


class Type(object):
    """See the later define Type variable for details."""
    definedTypes = {}
    def __getattr__(self, name):
        if name in _name_to_code:
            return Member(_name_to_code[name])
        if name in self.definedTypes:
            return CompoundMember(self.definedTypes[name])


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
Type=Type()


class MetaCompoundType(type):
    def __new__(cls, name, bases, d):
        if name in _name_to_code:
            raise TypeError("%r is a basic type" % name)

        # Get each Element field, sorted by id.
        byteOrder = d.pop("_byteOrder", Format.Native)
        elems = sorted(((k,v) for (k,v) in d.iteritems()
                        if isinstance(v, Member)),
                        key=lambda x:x[1].uid)

        class _D(object): pass
        v = _D()
        v.offset = 0
        v.ct_info = {}
        v.ct_alignment = 1
        v.ct_size = 0
        for idx, (memberName, memberType) in enumerate(elems):
            memberType.setDefByteOrder(byteOrder)
        cls.grok_members(elems, v)

        for n in d.copy():
            if isinstance(d[n], Member):
                del d[n]

        klass = type.__new__(cls, name, bases, d)
        klass._meta = ClassMetaInfo(klass, None)
        klass._meta.size = v.ct_size
        klass._meta.ct_info = v.ct_info
        klass._meta.ct_alignment = v.ct_alignment

        if name not in ("type", "Struct", "Union"):
            Type.definedTypes[name] = klass
        return klass


class MetaStructType(MetaCompoundType):
    def __new__(cls, name, bases, d):
        klass = super(MetaStructType, cls).__new__(cls, name, bases, d)
        klass._meta.compTypeName = "struct"
        return klass

    @classmethod
    def grok_members(cls, elems, v):
        prev_type = None
        start_bit = None
        bit_fld_size = None
        fillSize = v.ct_size = offset = 0
        bitMemberName = None #: The member providing the bits
        bitMemberType = None #: The type of the member providing the bits.

        for idx, (memberName, memberType) in enumerate(elems):
            if memberType._isBitField:
                if bitMemberType is not None:
                    if bitMemberType.hasRoom(memberType):
                        bitMemberType.makeFld(memberType)
                        # print("a>>>", memberName, "off", offset, "size", memberType._size)
                    else:
                        offset = fillSize
                        memberType.makeFld(memberType)
                        bitMemberName, bitMemberType = memberName, memberType
                        # print("b>>>", memberName, "off", offset, "size", memberType._size)
                else:
                    offset = fillSize
                    memberType.makeFld(memberType)
                    bitMemberName, bitMemberType = memberName, memberType
            else:
                offset = fillSize
                bitMemberName, bitMemberType = None, None

            assert memberType.alignment in (1, 2, 4)
            assert v.ct_alignment in (1, 2, 4)

            # Adjust the offset to suit the member's alignment requirements
            while offset % memberType.alignment != 0:
                offset += 1
            v.ct_alignment = max(v.ct_alignment, memberType.alignment)
            v.ct_size = fillSize = max(fillSize, offset + memberType._size)
            while v.ct_size % v.ct_alignment != 0:
                v.ct_size += 1

            v.ct_info[memberName] = idx, memberType, offset
            assert v.ct_alignment in (1, 2, 4)
            # print("C>>>", memberName, "off", offset, "size", memberType._size, memberType.alignment, v.ct_size, fillSize)
            # offset += memberType._size
            a, b, c = v.ct_info[memberName]
            # print("E>>>", memberName, "off", c, memberType._isBitField, memberType.alignment, v.ct_size, fillSize)


class MetaUnionType(MetaCompoundType):
    def __new__(cls, name, bases, d):
        klass = super(MetaUnionType, cls).__new__(cls, name, bases, d)
        klass._meta.compTypeName = "union"
        return klass

    @classmethod
    def grok_members(cls, elems, v):
        for idx, (memberName, memberType) in enumerate(elems):
            v.ct_alignment = max(v.ct_alignment, memberType.alignment)
            v.ct_size = max(v.ct_size, memberType._size)
            while v.ct_size % v.ct_alignment != 0:
                v.ct_size += 1
            v.ct_info[memberName] = idx, memberType, v.offset


class Compound(object):
    """The base class for the C-struct classes.

    This provides the basis for the `Struct` and `Union` classes, which in turn
    should be specialised by the user to define Python classes that effectively
    emulate C compound types.
    """
    def __init__(self, _rawData=None, trim=False, **kwargs):
        self.__dict__["_meta"] = InstanceMetaInfo(self)
        if _rawData is not None:
            self._meta.setBytes(_rawData, trim=trim)
        else:
            self._meta.setBytes(_makeBytes(self._meta.size))
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __getattr__(self, name):
        return _getA(name, self.__class__, self._meta.bytes)

    def __setattr__(self, name, v):
        _setA(name, self.__class__, self._meta.bytes, v)

    def _dup(self, trim=1): #pragma: to test
        return self.__class__(self._meta.s, trim=trim)

    def __getstate__(self): #pragma: to test
        return self._meta.bytes

    def __setstate__(self, v): #pragma: to test
        self._meta.bytes = v


class Union(Compound):
    """The base class used to define the equivalent of C structs.

    The user guide in this module's documentation provides useful examples,
    but basically to define a Python class to map to a C-union you do
    something like::

        # Python like this                      # is equivalent to C like this
        class MsgBody(Union):                   # struct MsgBody {
            text   = Type.String[256]           #    char text[256];
            values = Type.UnsignedShort[50]     #    unsigned short[50];
                                                # };

    The `Struct` class provides an example of using such a union within a
    structure.
    """
    __metaclass__ = MetaUnionType


class Struct(Compound):
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


class ProxyCompound(object):
    def __init__(self, bytes, myType, offset):
        self.__dict__["_meta"] = InstanceMetaInfo(self, bytes)
        self._meta.size = myType._meta.size
        self._meta.myType = myType
        self._meta.offset = offset
        self._meta.ct_info = myType._meta.ct_info

    def __str__(self):
        return "Proxy:%d" % self._meta.offset

    def __getattr__(self, name):
        return _getA(name, self._meta.myType, self._meta.bytes, self._meta.offset)

    def __setattr__(self, name, v):
        _setA(name, self._meta.myType, self._meta.bytes, v, self._meta.offset)


class ProxyArray(object):
    def __init__(self, bytes, arrType, offset):
        self.__dict__["_meta"] = ArrayMeta(self, bytes)
        self._meta.dimension = arrType._meta.dimension
        self._meta.elementSize = arrType._meta.elementSize
        self._meta.elementType = arrType._meta.elementType
        self._meta.offset = offset
        self._meta.size = arrType._meta.size

    def __str__(self):
        return "Array[%d] at offset=%d" % (self._meta.dimension,
                self._meta.offset)

    def __getitem__(self, idx):
        return _getA2(self._meta.elementType, self._meta.bytes,
                self._meta.calcArrayByteOffest(idx))

    def __setitem__(self, idx, v):
        return _setA2(self._meta.elementType, self._meta.bytes, v,
                self._meta.calcArrayByteOffest(idx))


def _getA(name, vType, bytes, baseOffset=0):
    if name not in vType._meta.ct_info:
        raise AttributeError(name)
    idx, memberType, offset = vType._meta.ct_info[name]
    offset += baseOffset
    return _getA2(memberType, bytes, offset)


def _getA2(memberType, bytes, offset):
    if isinstance(memberType, CompoundMember):
        return ProxyCompound(bytes, memberType.struct, offset)

    if isinstance(memberType, ArrayMember):
        return ProxyArray(bytes, memberType, offset)

    if memberType._bits is not None:
        mt = memberType._bit_src or memberType
        s = bytes[offset:offset+mt._size]
        if len(s) < mt._size:
            s.extend(_makeBytes(mt._size - len(s)))
    else: #pragma: to test
        s = bytes[offset:offset+memberType._size]
        if len(s) < memberType._size:
            s.extend(_makeBytes(memberType._size - len(s)))
    v = memberType.unpack(s)
    try:
        v._meta.offset = offset
    except AttributeError:
        pass
    return v


def _setA(name, vType, bytes, v, baseOffset=0):
    if name not in vType._meta.ct_info:
        raise AttributeError(name)
    idx, memberType, offset = vType._meta.ct_info[name]
    offset += baseOffset
    _setA2(memberType, bytes, v, offset)


def _setA2(memberType, bytes, v, offset):
    if isinstance(memberType, CompoundMember):
        if isinstance(v, Struct):
            if memberType.struct != v.__class__:
                raise TypeError("TODO - wrong type")
            bytes[offset:offset+v._meta.size] = v._meta.bytes
        elif isinstance(v, ProxyCompound):
            if memberType.struct != v._meta.myType:
                raise TypeError("TODO - mismatch")
            bytes[offset:offset+v._meta.myType._meta.size] = v._meta.bytes[
                    v._meta.offset:v._meta.offset+v._meta.myType._meta.size]
        else:
            raise TypeError("TODO")

        return

    bitSource = memberType
    if memberType._isBitField:
        bitSource = memberType._bit_src or memberType
        cur_v = bitSource.unpack(bytes[offset:offset + bitSource._size],
                mask=False)

        m1 = _masks[memberType._bits - 1] << memberType._start_bit
        v = (cur_v & (0xFFFFFFFFFFFFFFFF ^ m1)) | ((v << memberType._start_bit) & m1)

    if offset + memberType._size > len(bytes):
        bytes.extend(_makeBytes(offset + memberType._size - len(bytes)))
    bytes[offset:offset+bitSource._size] = array("B", bitSource.pack(v))


_masks = {}
m = 0x0000000000000000
for i in range(64):
    m = (m << 1) | 1
    _masks[i] = m
del i, m
