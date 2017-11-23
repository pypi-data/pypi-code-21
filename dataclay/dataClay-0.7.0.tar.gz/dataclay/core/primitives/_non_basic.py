from datetime import date

from dataclay import runtime
from ._basic import Serializable, PrimitiveType, Int, Vlq, Str, Bool, DCID
from .. import logger
from collections import Sequence, Mapping
import cPickle as pickle
__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

import re


class Dict(PrimitiveType):
    """Basic dictionary."""
    __slots__ = ("_type_key", "_type_value", "_size_by_vlq")

    def __init__(self, type_key, type_value, size_by_vlq=False):
        """Define a new dictionary serialization/deserialization instance."""
        self._type_key = type_key
        self._type_value = type_value
        self._size_by_vlq = size_by_vlq

    def read(self, io_file):
        ret = dict()
        if self._size_by_vlq:
            size = Vlq().read(io_file)
        else:
            size = Int(32).read(io_file)
        for _ in range(size):
            k = self._type_key.read(io_file)
            ret[k] = self._type_value.read(io_file)
        return ret

    def write(self, io_file, value):
        assert isinstance(value, Mapping)
        size = len(value)
        if self._size_by_vlq:
            Vlq().write(io_file, size)
        else:
            Int(32).write(io_file, size)

        for k, v in value.iteritems():
            self._type_key.write(io_file, k)
            self._type_value.write(io_file, v)


class List(PrimitiveType):
    """Basic list."""
    __slots__ = ("_type_items", "_size_by_vlq")

    def __init__(self, type_items, size_by_vlq=False):
        """Define a new list serialization/deserialization instance."""
        self._type_items = type_items
        self._size_by_vlq = size_by_vlq

    def read(self, io_file):
        ret = []
        if self._size_by_vlq:
            size = Vlq().read(io_file)
        else:
            size = Int(32).read(io_file)
        for _ in range(size):
            ret.append(self._type_items.read(io_file))
        return ret

    def write(self, io_file, value):
        assert isinstance(value, Sequence)
        size = len(value)
        if self._size_by_vlq:
            Vlq().write(io_file, size)
        else:
            Int(32).write(io_file, size)

        for item in value:
            self._type_items.write(io_file, item)


class Tuple(PrimitiveType):
    """In Java is assumed to be a Pair, but can be used as an arbitrary length (pythonic) tuple."""
    __slots__ = ("_types",)

    def __init__(self, *types):
        """Define the types for a tuple."""
        self._types = types

    def read(self, io_file):
        return [t.read(io_file) for t in self._types]

    def write(self, io_file, value):
        assert isinstance(value, Sequence)
        assert len(value) == len(self._types)
        for t, v in zip(self._types, value):
            t.write(io_file, v)


class Set(PrimitiveType):
    """Basic set."""
    __slots__ = ("_type_items", "_size_by_vlq")

    def __init__(self, type_items, size_by_vlq=False):
        """Define a new set serialization/deserialization instance."""
        self._type_items = type_items
        self._size_by_vlq = size_by_vlq

    def read(self, io_file):
        ret = set()
        if self._size_by_vlq:
            size = Vlq().read(io_file)
        else:
            size = Int(32).read(io_file)
        for _ in range(size):
            ret.add(self._type_items.read(io_file))
        return ret

    def write(self, io_file, value):
        assert isinstance(value, set) or isinstance(value, frozenset)
        size = len(value)
        if self._size_by_vlq:
            Vlq().write(io_file, size)
        else:
            Int(32).write(io_file, size)

        for item in value:
            self._type_items.write(io_file, item)


class BitMap(PrimitiveType):
    """dataClay BitMap, used in various places with various variants."""
    __slots__ = ("_serialize_nob", "_size")

    def __init__(self, serialize_nob=True, size=None):
        assert serialize_nob or size is not None, "If number of bytes is not serialized, you must provide a size"
        self._serialize_nob = serialize_nob
        self._size = size

    def read(self, io_file):
        if self._serialize_nob:
            nob = Int(16).read(io_file)
            assert self._size is None or self._size < nob * 8
            if self._size is not None:
                size = self._size
            else:
                size = nob * 8
        else:
            size = self._size
            nob = (size - 1) / 8 + 1

        source_bytes = io_file.read(nob)
        ret = [False] * size

        for i in range(size):
            if (ord(source_bytes[nob - 1 - (i / 8)]) & (0x01 << (i % 8))) != 0:
                ret[i] = True
        return ret

    def write(self, io_file, value):
        assert self._size is None or len(value) == self._size

        nob = (len(value) - 1) / 8 + 1  # number of bytes required
        ba = bytearray(nob)

        if self._serialize_nob:
            Int(16).write(io_file, nob)

        for i in range(len(value)):
            if value[i]:
                ba[nob - 1 - (i / 8)] |= 0x01 << (i % 8)
        io_file.write(ba)


class Calendar(PrimitiveType):
    """Calendar-based YEAR/MONTH/DAY_OF_MONTH.

    Uses datetime.date internally.
    """
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        year = Int(32).read(io_file)
        month = Int(32).read(io_file)
        day_of_month = Int(32).read(io_file)
        return date(year, month, day_of_month)

    def write(self, io_file, value):
        assert isinstance(value, date)
        Int(32).write(io_file, date.year)
        Int(32).write(io_file, date.month)
        Int(32).write(io_file, date.day)


class PyTypeWildcard(PrimitiveType):
    """Generic catch-all for Python types (including custom-signature binary types)."""
    __slots__ = ("_signature", "_pickle_fallback")

    PYTHON_PREFIX = 'python.'

    # Note that this regex does not have guarantees on matching <> or [] (so <] will be a valid group,
    # as so will be its [> counterpart). But... that seems a user problem.
    # Also: deep and esoteric nesting is not supported (regex should be thrown away and a sane
    # markup reader used instead).
    SEQUENCE_REGEX = re.compile(r'(?P<base_type>(list)|(tuple))\s*(?:[<\[]\s*(?P<subtype>.*?)\s*[>\]])?\s*$')
    MAPPING_REGEX = re.compile(r'(?P<base_type>dict)\s*(?:[<\[]\s*(?P<keytype>.*?)\s*,\s*(?P<valuetype>.*?)\s*[>\]])?\s*$')
    STR_SIGNATURE = 'str'
    UNICODE_SIGNATURE = 'unicode'
    STORAGEOBJECT_SIGNATURE = 'storageobject'
    ANYTHING_SIGNATURE = 'anything'
    ANYTHING_ALIAS_PREFIX = ['numpy']

    def __init__(self, signature, pickle_fallback=False):
        # TODO make some checks, and raise InvalidPythonSignature otherwise
        self._signature = signature
        self._pickle_fallback = pickle_fallback

    def read(self, io_file):
        from dataclay.core.management.classmgr import serialization_types
        try:
            return serialization_types[self._signature].read(io_file)
        except KeyError:
            pass

        # anything is also a special case, also all its alias
        if self._signature == self.ANYTHING_SIGNATURE or \
                self._signature == self.STORAGEOBJECT_SIGNATURE or \
                any(self._signature.startswith(aa)
                    for aa in self.ANYTHING_ALIAS_PREFIX):
            field_size = Int(32).read(io_file)
            return pickle.loads(io_file.read(field_size))

        # Everything shoulda be a python type...
        if not self._signature.startswith(self.PYTHON_PREFIX):
            # ... except the fallbacks (mostly for subtypes like lists of persistent objects)
            assert self._pickle_fallback
            field_size = Int(32).read(io_file)
            return pickle.loads(io_file.read(field_size))

        subtype = self._signature[len(self.PYTHON_PREFIX):]

        sequence_match = self.SEQUENCE_REGEX.match(subtype)
        mapping_match = self.MAPPING_REGEX.match(subtype)

        if sequence_match:
            gd = sequence_match.groupdict()
            logger.debug("Deserializing a Python Sequence with the following match: %s", gd)

            if gd["subtype"]:
                instances_type = PyTypeWildcard(gd["subtype"], pickle_fallback=True)
            else:  # list without subtypes information
                instances_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)

            ret = list()
            size = Int(32).read(io_file)
            for i in range(size):
                if Bool().read(io_file):
                    ret.append(instances_type.read(io_file))
                else:
                    ret.append(None)

            if gd["base_type"] == "tuple":
                return tuple(ret)
            else:
                return ret

        elif mapping_match:
            gd = mapping_match.groupdict()
            logger.debug("Deserializing a Python mapping with the following match: %s", gd)

            if gd["keytype"] and gd["valuetype"]:
                key_type = PyTypeWildcard(gd["keytype"], pickle_fallback=True)
                value_type = PyTypeWildcard(gd["valuetype"], pickle_fallback=True)
            else:
                # dict without subtypes information
                key_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)
                value_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)

            ret = dict()
            size = Int(32).read(io_file)
            for i in range(size):
                if Bool().read(io_file):
                    key = key_type.read(io_file)
                else:
                    key = None

                if Bool().read(io_file):
                    ret[key] = value_type.read(io_file)
                else:
                    ret[key] = None
            return ret

        elif subtype == self.STR_SIGNATURE:
            return Str('binary').read(io_file)
        elif subtype == self.UNICODE_SIGNATURE:
            return Str('utf-16').read(io_file)
        else:
            raise NotImplementedError("Python types supported at the moment: "
                                      "list and mappings (but not `%s`), sorry" % subtype)

    def write(self, io_file, value):

        from dataclay.core.management.classmgr import serialization_types
        try:
            serialization_types[self._signature].write(io_file, value)
            return
        except KeyError:
            pass

        # anything is also a special case, also all its alias
        if self._signature == self.ANYTHING_SIGNATURE or \
                self._signature == self.STORAGEOBJECT_SIGNATURE or \
                any(self._signature.startswith(aa)
                    for aa in self.ANYTHING_ALIAS_PREFIX):
            s = pickle.dumps(value)
            Int(32).write(io_file, len(s))
            io_file.write(s)
            return

        # Everything shoulda be a python type...
        if not self._signature.startswith(self.PYTHON_PREFIX):
            # ... except the fallbacks (mostly for subtypes like lists of persistent objects)
            assert self._pickle_fallback
            s = pickle.dumps(value)
            Int(32).write(io_file, len(s))
            io_file.write(s)
            return

        # Now everything must be a python type
        assert self._signature.startswith(self.PYTHON_PREFIX), \
            "Signature for Python types is expected to start with " \
            "'python'. Found signature: %s" % self._signature

        subtype = self._signature[len(self.PYTHON_PREFIX):]

        sequence_match = self.SEQUENCE_REGEX.match(subtype)
        mapping_match = self.MAPPING_REGEX.match(subtype)

        if sequence_match:
            gd = sequence_match.groupdict()
            logger.debug("Serializing a Python Sequence with the following match: %s", gd)

            if gd["subtype"]:
                instances_type = PyTypeWildcard(gd["subtype"], pickle_fallback=True)
            else:  # list without subtypes information
                instances_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)

            Int(32).write(io_file, len(value))
            for elem in value:
                if elem is None:
                    Bool().write(io_file, False)
                else:
                    Bool().write(io_file, True)
                    instances_type.write(io_file, elem)

        elif mapping_match:
            gd = mapping_match.groupdict()
            logger.debug("Serializing a Python Mapping with the following match: %s", gd)

            if gd["keytype"] and gd["valuetype"]:
                key_type = PyTypeWildcard(gd["keytype"], pickle_fallback=True)
                value_type = PyTypeWildcard(gd["valuetype"], pickle_fallback=True)
            else:  # dict without subtypes information
                key_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)
                value_type = PyTypeWildcard(self.ANYTHING_SIGNATURE)

            Int(32).write(io_file, len(value))

            for key, value in value.iteritems():
                if key is None:
                    Bool().write(io_file, False)
                else:
                    Bool().write(io_file, True)
                    key_type.write(io_file, key)

                if value is None:
                    Bool().write(io_file, False)
                else:
                    Bool().write(io_file, True)
                    value_type.write(io_file, value)

        elif subtype == self.STR_SIGNATURE:
            Str('binary').write(io_file, value)
        elif subtype == self.UNICODE_SIGNATURE:
            Str('utf-16').write(io_file, value)
        else:
            raise NotImplementedError("Python types supported at the moment: "
                                      "list and mappings (but not `%s`), sorry" % subtype)


class IfaceBitMaps(PrimitiveType):
    """Interface BitMap."""
    __slots__ = ()

    def __init__(self):
        pass

    def read(self, io_file):
        if not (Bool().read(io_file)):
            return None
        ret = dict()
        size = Int(32).read(io_file)
        for i in range(size):
            oid = DCID().read(io_file)
            ret[oid] = Str("binary").read(io_file)

        return ret

    def write(self, io_file, value):
        if value is None:
            Bool().write(io_file, False)
            return
        else:
            Bool().write(io_file, True)

        Int(32).write(io_file, len(value))

        for mc_id, ba in value.iteritems():
            DCID().write(io_file, mc_id)
            Str("binary").write(io_file, ba)
