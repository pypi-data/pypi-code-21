from struct import Struct
import uuid
from io import BytesIO

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class Serializable(object):
    __slots__ = ()


class PrimitiveType(Serializable):
    __slots__ = ()


class NotImplementedType(PrimitiveType):
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        raise NotImplementedError("Trying to deserialize something not implemented")

    def write(self, io_file, value):
        raise NotImplementedError("Trying to serialize something not implemented")


class Null(PrimitiveType):
    """Null empty type."""
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        return None

    def write(self, io_file, value):
        pass


class Int(PrimitiveType):
    """Multiple-size integer type."""
    __slots__ = ("_size", "_type")

    sizes = {8: Struct("!b"),
             16: Struct("!h"),
             32: Struct("!i"),
             64: Struct("!q")}

    def __init__(self, size=32):
        assert size in self.sizes, "Invalid size {:d} for integer type".format(size)
        self._size = size
        self._type = self.sizes[size]

    def read(self, io_file):
        val = io_file.read(self._size / 8)
        return self._type.unpack(val)[0]

    def write(self, io_file, value):
        io_file.write(self._type.pack(value))


class Vlq(PrimitiveType):
    """Variable Length Quantity."""
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        value = 0
        while True:
            # Read one byte and build
            b = ord(io_file.read(1))
            value = (value << 7) + (b & 0x7F)

            # If the continuation bit (MSB) is zero, we are finished
            if (b & 0x80) == 0:
                return value

    def write(self, io_file, value):
        if value == 0:
            io_file.write(chr(0x00))
            return
        values = []
        while value > 0:
            # Put the 7-bit values into the list
            values.append(value & 0x7F)
            value >>= 7

        # Values with continuation bit activated
        for b in reversed(values[1:]):
            io_file.write(chr(0x80 | b))

        # Last value, no continuation bit
        io_file.write(chr(values[0]))


class Float(PrimitiveType):
    """Single or double precision floating value type."""
    __slots__ = ("_size", "_type")

    sizes = {32: Struct("!f"),
             64: Struct("!d")}

    def __init__(self, size=32):
        assert size in self.sizes, "Invalid size {:d} for integer type".format(size)
        self._size = size
        self._type = self.sizes[size]

    def read(self, io_file):
        val = io_file.read(self._size / 8)
        return self._type.unpack(val)[0]

    def write(self, io_file, value):
        io_file.write(self._type.pack(value))


class Str(PrimitiveType):
    """String with different modes/encodings."""
    __slots__ = ("_mode", "_nullable")

    modes = {"utf-8", "utf-16", "binary"}

    def __init__(self, mode="utf-16", nullable=False):
        assert mode in self.modes, "The String mode should be one in {}".format(self.modes)
        self._mode = mode
        self._nullable = nullable

    def read(self, io_file):
        if self._nullable:
            is_not_null = Bool().read(io_file)
            if not is_not_null:
                return None

        size = Int(32).read(io_file)
        ba = io_file.read(size)

        if self._mode == "utf-8":
            return ba.decode('utf-8')
        elif self._mode == "utf-16":
            return ba.decode('utf-16-be')
        elif self._mode == "binary":
            return ba
        else:
            raise TypeError("Internal mode {} not recognized".format(self._mode))

    def write(self, io_file, value):
        if self._nullable:
            if value is None:
                Bool().write(io_file, False)
                return
            else:
                Bool().write(io_file, True)

        if self._mode == "utf-8":
            ba = value.encode('utf-8')
        elif self._mode == "utf-16":
            ba = value.encode('utf-16-be')
        elif self._mode == "binary":
            if isinstance(value, BytesIO):
                ba = value.getvalue()
            else:
                ba = bytes(value)
        else:
            raise TypeError("Internal mode {} not recognized".format(self._mode))

        Int(32).write(io_file, len(ba))
        io_file.write(ba)


class Bool(PrimitiveType):
    """One-byte bool type (0 means False)."""
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        val = Int(8).read(io_file)
        if val == 0:
            return False
        else:
            return True

    def write(self, io_file, value):
        if value:
            Int(8).write(io_file, 0x01)
        else:
            Int(8).write(io_file, 0x00)


class DCID(PrimitiveType):
    """dataClay UUID (straightforward serialization)."""
    __slots__ = ("_nullable", )

    def __init__(self, nullable=False):
        self._nullable = nullable

    def read(self, io_file):
        if self._nullable:
            present = Bool().read(io_file)
            if not present:
                return None
        return uuid.UUID(bytes=str(io_file.read(16)))

    def write(self, io_file, value):
        if self._nullable:
            if value is None:
                Bool().write(io_file, False)
                return
            else:
                Bool().write(io_file, True)

        io_file.write(value.get_bytes())
