from ctypes import (addressof, cast, sizeof, Array, POINTER,
                    c_uint8, c_uint16, c_uint32, c_uint64,
                    c_int8, c_int16, c_int32, c_int64,
                    c_float, c_double)
from six import string_types

import flatbuffers
from flatbuffers import number_types as N


def CreateString(self, s, encoding='utf-8'):
    """CreateString writes a null-terminated byte string as a vector."""

    self.assertNotNested()
    self.nested = True

    if not isinstance(s, string_types):
        raise TypeError("non-string passed to CreateString")

    encoded_string = s.encode(encoding)

    self.Prep(N.UOffsetTFlags.bytewidth,
              (len(encoded_string) + 1) * N.Uint8Flags.bytewidth)
    self.Place(0, N.Uint8Flags)

    length = N.UOffsetTFlags.py_type(len(s))

    self.head = N.UOffsetTFlags.py_type(self.Head() - length)
    self.Bytes[self.Head():self.Head() + length] = encoded_string

    return self.EndVector(len(encoded_string))

flatbuffers.builder.Builder.CreateString = CreateString


def CreateVector(self, element_type, v):
    """Writes a list or array to the buffer, using ctypes arrays."""
    _flags = {
        c_uint8: N.Uint8Flags,
        c_uint16: N.Uint16Flags,
        c_uint32: N.Uint32Flags,
        c_uint64: N.Uint64Flags,
        c_int8: N.Int8Flags,
        c_int16: N.Int16Flags,
        c_int32: N.Int32Flags,
        c_int64: N.Int64Flags,
        c_float: N.Float32Flags,
        c_double: N.Float64Flags,
    }

    self.assertNotNested()
    self.nested = True

    flags = _flags[element_type]
    nelements = len(v)
    nbytes = nelements * flags.bytewidth

    # ensure or cast v to array of element_types
    if not isinstance(v, Array):
        v = (element_type * nelements)(*v)
        p = cast(v, POINTER(element_type))
    elif not isinstance(v, element_type * nelements):
        nbytes = nelements * sizeof(v._type_)
        nelements, r = divmod(nbytes, sizeof(element_type))
        if r:
            raise TypeError('could not cast array to the requested type')
        p = cast(v, POINTER(element_type))
        v = (element_type * nelements)(*[p[i] for i in range(nelements)])

    self.Prep(N.UOffsetTFlags.bytewidth, nbytes * flags.bytewidth)
    self.Place(0, flags)
    length = N.UOffsetTFlags.py_type(nelements)
    self.head = N.UOffsetTFlags.py_type(self.Head() - length)

    # Reallocate the buffer if needed
    while self.Head() < N.UOffsetTFlags.bytewidth:
        oldBufSize = len(self.Bytes)
        self.growByteBuffer()
        updated_head = self.head + len(self.Bytes) - oldBufSize
        self.head = N.UOffsetTFlags.py_type(updated_head)

    self.Bytes[self.Head():self.Head() + length] = v
    return self.EndVector(nelements)

flatbuffers.Builder.CreateVector = CreateVector


def GetVector(self, offset, element_type, j=None):
    o = flatbuffers.number_types.UOffsetTFlags.py_type(self.Offset(offset))
    if o:
        a = self.Vector(o)
        if j is None:
            addr = addressof(cast(self.Bytes, POINTER(c_int8)).contents) + a
            return (element_type * self.VectorLen(o)).from_address(addr)
        else:
            off = a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1)
            return self.Get(flatbuffers.number_types.Int8Flags, offs)
    else:
        return [] if j is None else 0

flatbuffers.table.Table.GetVector = GetVector
