# -*-coding: utf-8 -*-
from collections import OrderedDict
from struct import pack
from .udst import UserInt, UserBytes, UserDict, UserList


class BencodeError(Exception):
    pass

class BencodeTypeError(TypeError):
    pass


class BencodeElement:
    @classmethod
    def load(cls, bstream):
        raise NotImplemented

    @classmethod
    def from_origin(cls, value):
        raise NotImplemented

    def __init__(self, value):
        self.bcode_value = value

    @classmethod
    def element_check(cls, element):
        if not issubclass(type(element), cls):
            raise BencodeTypeError("{0} is not a valid {1} element".format(type(element).__name__, cls.__name__))

    @property
    def parsed(self):
        return self.bcode_value

    def to_origin(self):
        return self.parsed

    def dump(self):
        raise NotImplemented

    def __len__(self):
        return len(self.bcode_value)


    def __str__(self):
        return str(self.bcode_value)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, str(self.bcode_value))


class Bint(BencodeElement, UserInt):
    Bcode_Decode_Table = set(b"i")

    @classmethod
    def load(cls, bstream):
        """
        Load Bint instance from original bencode stream.
        :param bstream: bencode stream in Python`s original bytes instance
        :return: (Bint, bytes(the rest of the input b encode stream))
        """

        accepted_char = set(b"1234567890")
        buffer = []
        if bstream and bstream.startswith(b"i"):
            for i in range(1, len(bstream)):
                if bstream[i] in accepted_char:
                    buffer.append(bstream[i])
                else:
                    if bstream[i] == ord("-") and i==1:
                        # Avoid invalid bstream like  i1-e or i-1-e.
                        buffer.append(bstream[i])
                    elif bstream[i] == ord("e"):
                        # Avoid invalid bstream like  i-e.
                        if not set(buffer) & accepted_char:
                            raise BencodeError("Invalid Bcode stream")
                        else:
                            return cls(int("".join((chr(i) for i in buffer)))), bstream[i+1:]
                    else:
                        raise BencodeError("Invalid Bcode stream")
        else:
            raise BencodeError("Invalid Bcode stream")

    @classmethod
    def from_origin(cls, value):
        """
        Convert original Python`s int instance into Bint
        :param value:  int instance to convert
        :return: Bint instance
        """
        return cls(value)

    def __init__(self, value, *args):
        self.bcode_prefix = b"i"
        self.bcode_suffix = b"e"
        BencodeElement.__init__(self, int(value, *args))
        self.data = self.bcode_value

    def dump(self):
        """
        Dump Bint instance into original bencode stream
        :return: bencode stream in Python`s original bytes instance.
        """
        fmt = "c{0}sc".format(len(str(self.bcode_value).encode()))
        return pack(fmt, self.bcode_prefix, str(self.bcode_value).encode(), self.bcode_suffix)


class Bbytes(BencodeElement, UserBytes):
    Bcode_Decode_Table = set(b"123456789")

    @classmethod
    def load(cls, bstream):
        """
        Load Bbytes instance from original bencode stream.
        :param bstream: bencode stream in Python`s original bytes instance
        return: (Bbytes, bytes(the rest of the input bencode stream))
        """
        if bstream:
            accepted_char = set(b"1234567890")
            buffer = []
            for i in range(len(bstream)):
                if bstream[i] in accepted_char:
                    buffer.append(chr(bstream[i]))
                else:
                    if bstream[i] == ord(":"):
                        bbyte_length = int("".join(buffer))
                        return cls(bstream[i + 1: i + 1 + bbyte_length]), bstream[i + 1 + bbyte_length:]
                    else:
                        raise BencodeError("Invalid Bcode stream")

    @classmethod
    def from_origin(cls, value):
        """
        Convert original Python`s bytes instance into Bytes
        :param value:  bytes instance to convert
        :return: Bytes instance
        """
        return cls(value)

    def __init__(self, *args, **kargs):
        self.sep = b":"
        super(Bbytes, self).__init__(bytes(*args, **kargs))
        self.data = self.bcode_value

    def __and__(self, other):
        if isinstance(other, self.__class__):
            v = other.data
        else:
            v = other
        rjust_width = max(len(v), len(self.data))
        rjusted_v, rjusted_data = v.rjust(rjust_width, b"\x00"), self.rjust(rjust_width, b"\x00")
        return self.__class__(bytes(rjusted_v[i] & rjusted_data[i] for i in range(rjust_width)))

    def __or__(self, other):
        if isinstance(other, self.__class__):
            v = other.data
        else:
            v = other
        rjust_width = max(len(v), len(self.data))
        rjusted_v, rjusted_data = v.rjust(rjust_width, b"\x00"), self.rjust(rjust_width, b"\x00")
        return self.__class__(bytes(rjusted_v[i] | rjusted_data[i] for i in range(rjust_width)))

    def __xor__(self, other):
        if isinstance(other, self.__class__):
            v = other.data
        else:
            v = other
        rjust_width = max(len(v), len(self.data))
        rjusted_v, rjusted_data = v.rjust(rjust_width, b"\x00"), self.rjust(rjust_width, b"\x00")
        return self.__class__(bytes(rjusted_v[i] ^ rjusted_data[i] for i in range(rjust_width)))

    def dump(self):
        """
        Dump Bbytes instance into original bencode stream
        :return: bencode stream in Python`s original bytes instance.
        """
        fmt = "{0}sc{1}s".format(len(str(len(self))), len(self))
        return pack(fmt, str(len(self)).encode(), self.sep, self.bcode_value)


class Blist(BencodeElement, UserList):
    Bcode_Decode_Table = set(b"l")
    @classmethod
    def load(cls, bstream):
        """
        Load Blist instance from original bencode stream.
        :param bstream: bencode stream in Python`s original bytes instance
        return: (Blist, bytes(the rest of the input bencode stream))
        """
        cache = []
        bs = bstream[1:]
        while bs:
            if bs.startswith(b"e"):
                return cls(cache), bs[1:]
            else:
                for element in BencodeElement.__subclasses__():
                    if bs[0] in element.Bcode_Decode_Table:
                        break
                else:
                    raise BencodeError("Invalid Bcode stream")
                parsed, bs = element.load(bs)
                cache.append(parsed)

    @classmethod
    def from_origin(cls, value):
        """
        Convert original Python`s  iterable to Blist. The iterable must only contain
        int, bytes, str, dict or iterable  instances that only contain those data structures mentioned.
        :param value:  iterable to convert
        :return: Blist instance
        """
        return cls(CASCADE(i) for i in value)

    def __init__(self, value):
        self.bcode_prefix = b"l"
        self.bcode_suffix = b"e"
        if hasattr(value, "__iter__"):
            v = value
        else:
            v = [value]
        BencodeElement.__init__(self, list(CASCADE(i) for i in v))
        self.data = self.bcode_value

    @property
    def parsed(self):
        return [i.parsed for i in self.bcode_value]

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(other.data + self.data)
        return type(other)(other + self.data)

    def __setitem__(self, key, value):
        v = value
        try:
            BencodeElement.element_check(v)
        except BencodeTypeError:
            v = CASCADE(value)
        UserList.__setitem__(self, key, v)

    def append(self, item):
        i = item
        try:
            BencodeElement.element_check(i)
        except BencodeTypeError:
            i = CASCADE(item)
        UserList.append(self, i)

    def extend(self, other):
        if not hasattr(other, "__iter__"):
            v = [other]
        else:
            v = other
        for item in v:
            BencodeElement.element_check(item)
        else:
            UserList.extend(self, other)

    def dump(self):
        bcode_value_bytes = b"".join(i.dump() for i in self.bcode_value)
        fmt = "c{0}sc".format(len(bcode_value_bytes))
        return pack(fmt, self.bcode_prefix, bcode_value_bytes, self.bcode_suffix)


class Bdict(BencodeElement, UserDict):
    Bcode_Decode_Table = set(b"d")

    @classmethod
    def load(cls, bstream):
        """
        Load Bdict instance from original bencode stream.
        :param bstream: bencode stream in Python`s original bytes instance
        return: (Bdict, bytes(the rest of the input bencode stream))
        """

        cache = {}

        bs = bstream[1:]
        while bs:
            if bs.startswith(b"e"):
                return cls(**cache), bs[1:]
            else:
                # We get the key first. The keys ought to be Bbyte.
                k, rest = Bbytes.load(bs)
                for element in BencodeElement.__subclasses__():
                    if rest[0] in element.Bcode_Decode_Table:
                        break
                else:
                    raise BencodeError("Invalid Bcode stream")
                # Then process the value.
                v, bs = element.load(rest)
                cache[k.parsed.decode()] = v

    @classmethod
    def from_origin(cls, value):
        """
        Convert original Python`s  dict to Bdict. The iterable must only contain
        int, bytes, str, dict or iterable  instances that only contain those data structures mentioned.
        :param value:  dict to convert
        :return: Bdict instance
        """
        return cls(**{str(k): CASCADE(v) for (k, v) in value.items()})

    def __init__(self, **kargs):
        self.bcode_prefix = b"d"
        self.bcode_suffix = b"e"
        BencodeElement.__init__(self, {k: CASCADE(v) for k, v in kargs.items()})
        self.data = self.bcode_value

    @property
    def parsed(self):
        return OrderedDict((k, self.bcode_value[k].parsed) for k in sorted(self.bcode_value.keys()))

    def iloc(self, index):
        """
        Get item by index. Bdict will  store values by the alphabet order of their keys.
        :param index:  index
        :return: the corresponding value(s)
        """
        try:
            return self.bcode_value[sorted(self.bcode_value.keys())[index]]
        except IndexError:
            raise IndexError("Bdict index out of range")

    def __setitem__(self, key, value):
        v = value
        try:
            BencodeElement.element_check(v)
        except BencodeTypeError:
            v = CASCADE(value)
        UserDict.__setitem__(self, key, v)

    def dump(self):
        bcode_value_bytes = b"".join(b"".join((Bbytes(k.encode()).dump(), self.bcode_value[k].dump()))
                                     for k in sorted(self.bcode_value.keys()))
        fmt = "c{0}sc".format(len(bcode_value_bytes))
        return pack(fmt, self.bcode_prefix, bcode_value_bytes, self.bcode_suffix)


class Bdecoder:
    def __init__(self):
        self.result = []

    @property
    def parsed(self):
        return self.result

    def parse(self, bstream):
        bs = bstream
        while bs:
            for element in BencodeElement.__subclasses__():
                if bs[0] in element.Bcode_Decode_Table:
                    break
            else:
                raise BencodeError("Invalid Bcode stream")
            parsed, bs = element.load(bs)
            self.result.append(parsed)


CASCADE_MAP = {
            int: Bint.from_origin,
            bytes: Bbytes.from_origin,
            str: lambda x: Bbytes.from_origin(x.encode()),
            dict: Bdict.from_origin
        }

def CASCADE(o):
    if issubclass(type(o), BencodeElement):
        return o
    else:
        if type(o) in CASCADE_MAP:
            return CASCADE_MAP[type(o)](o)
        elif hasattr(o, "__iter__"):
            return Blist.from_origin(o)
        else:
            return CASCADE_MAP[str](str(o).encode())