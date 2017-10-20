# -*- coding:utf-8 -*-
# For backwards compatibility, continue to make the collections ABCs
# available through the collections module.
from _collections_abc import *
from collections import UserDict, UserString, UserList
import sys as _sys


class UserInt(object):
    """A more or less complete user-defined wrapper around int objects."""
    @classmethod
    def from_bytes(cls, bytes, byteorder, *args, **kwargs):
        return cls(int.from_bytes(bytes, byteorder))

    def __init__(self, *args, **kargs):
        if isinstance(args[0], int):
            self.data = args[0]
        elif isinstance(args[0], self.__class__):
            self.data = args[0].data
        else:
            self.data = int(*args, **kargs)

    def __abs__(self):
        return self.__class__(abs(self.data))

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data + other.data)
        return self.__class__(self.data + other)

    def __and__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data & other.data)
        return self.__class__(self.data & other)

    def __bool__(self):
        return bool(self.data)

    def __ceil__(self, *args, **kwargs):
        return self

    def __divmod__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(divmod(self.data, other.data))
        return self.__class__(divmod(self.data, other))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data == other.data)
        return self.__class__(self.data == other)

    def __float__(self):
        return float(self.data)

    def __floordiv__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data // other.data)
        return self.__class__(self.data // other)

    def __floor__(self, *args, **kwargs):
        return self

    def __getnewargs__(self, *args, **kwargs):
        return self

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data >= other.data)
        return self.__class__(self.data >= other)

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data > other.data)
        return self.__class__(self.data > other)

    def __hash__(self):
        return hash(self.data)

    def __index__(self):
        return self.data

    def __int__(self):
        return self.data

    def __invert__(self, *args, **kwargs):
        return self.__class__(-self.data)

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data <= other.data)
        return self.__class__(self.data <= other)

    def __lshift__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data << other.data)
        return self.__class__(self.data << other)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data < other.data)
        return self.__class__(self.data < other)

    def __mod__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data % other.data)
        return self.__class__(self.data % other)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data * other.data)
        return self.__class__(self.data * other)

    def __neg__(self, *args, **kwargs):
        return self.__class__(-self.data)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data != other.data)
        return self.__class__(self.data != other)

    def __or__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data | other.data)
        return self.__class__(self.data | other)

    def __pos__(self, *args, **kwargs):
        return self

    def __pow__(self, power, modulo=None):
        p = power.data if isinstance(power, self.__class__) else power
        m = modulo.data if isinstance(modulo, self.__class__) else modulo
        return self.__class__(pow(self.data, p, m))

    def __radd__(self, other):
        return type(other)(other + self.data)

    def __rand__(self, other):
        return type(other)(other & self.data)

    def __rdivmod__(self, other):
        return type(other)(divmod(other, self.data))

    def __repr__(self):
        return repr(self.data)

    def __rfloordiv__(self, other):
        return type(other)(other // self.data)

    def __rlshift__(self, other):
        return type(other)(other << self.data)

    def __rmod__(self, other):
        return type(other)(other % self.data)

    def __rmul__(self, other):
        return type(other)(other * self.data)

    def __ror__(self, other):
        return type(other)(other | self.data)

    def __round__(self, *args, **kwargs):
        return round(self.data, *args, **kwargs)

    def __rpow__(self, other, *args, **kargs):
        return type(other)(pow(other, self.data, *args, **kargs))

    def __rrshift__(self, other):
        return type(other)(other >> self.data)

    def __rshift__(self, other):
        return self.__class__(self.data >> other)

    def __rsub__(self, other):
        return type(other)(other - self.data)

    def __rtruediv__(self, other):
        return type(other)(other / self.data)

    def __rxor__(self, other):
        return type(other)(other ^ self.data)

    def __str__(self, *args, **kwargs):
        return str(self.data)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data - other.data)
        return self.__class__(self.data - other)

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data / other.data)
        return self.__class__(self.data / other)

    def __trunc__(self):
        return self

    def __xor__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data ^ other.data)
        return self.__class__(self.data ^ other)


class UserBytes(Sequence):
    def __init__(self, *args, **kargs):
        if isinstance(args[0], bytes):
            self.data = args[0]
        elif isinstance(args[0], self.__class__):
            self.data = args[0].data[:]
        else:
            self.data = bytes(*args, **kargs)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __float__(self): return float(self.data)
    def __hash__(self): return hash(self.data)
    def __getnewargs__(self):
        return (self.data[:],)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return self.data == value.data
        return self.data == value
    def __lt__(self, value):
        if isinstance(value, self.__class__):
            return self.data < value.data
        return self.data < value
    def __le__(self, value):
        if isinstance(value, self.__class__):
            return self.data <= value.data
        return self.data <= value
    def __gt__(self, value):
        if isinstance(value, self.__class__):
            return self.data > value.data
        return self.data > value
    def __ge__(self, value):
        if isinstance(value, self.__class__):
            return self.data >= value.data
        return self.data >= value

    def capitalize(self): return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, self.__class__):
            sub = sub.data
        return self.data.count(sub, start, end)

    def decode(self, decoding=None, errors=None): # XXX improve this?
        if decoding:
            if errors:
                return self.__class__(self.data.decode(decoding, errors))
            return self.__class__(self.data.decode(decoding))
        return self.__class__(self.data.decode())

    def endswith(self, suffix, start=0, end=_sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, self.__class__):
            sub = sub.data
        return self.data.find(sub, start, end)

    @classmethod
    def fromhex(cls, string):
        return cls(bytes.fromhex(string))

    def hex(self):
        return self.data.hex()

    def index(self, sub, start=0, end=_sys.maxsize):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    maketrans = str.maketrans
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        if isinstance(old, self.__class__):
            old = old.data
        if isinstance(new, self.__class__):
            new = new.data
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, UserString):
            sub = sub.data
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=_sys.maxsize):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=False): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=_sys.maxsize):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data + other.data)
        return self.__class__(self.data + other)

    def __bool__(self):
        return bool(self.data)

    def __contains__(self, other):
        if isinstance(other, self.__class__):
            return other.data in self.data
        return other in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __mul__(self, other):
        return self.__class__(self.data * other)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data != other.data)
        return self.__class__(self.data != other)

    def __radd__(self, other):
        return type(other)(other + self.data)

    def __reversed__(self):
        return reversed(self.data)


