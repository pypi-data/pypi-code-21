"""Python definitions for consistent tuple-like behaviour of dataClay containers."""
from copy import copy
import logging
from dataclay.core.primitives import *

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


class ContainerMetaclass(type):
    def __new__(cls, name, bases, dct):
        if "_fields" not in dct:
            raise AttributeError("All container must have a `_fields` attribute")
        all_fields = [field[0] for field in dct["_fields"]]

        if "_internal_fields" in dct:
            all_fields += dct["_internal_fields"]
        dct["__slots__"] = tuple(all_fields)

        return super(ContainerMetaclass, cls).__new__(cls, name, bases, dct)


class GenericContainer(Serializable):
    """Provide basic serialization/deserialization mechanisms."""
    __metaclass__ = ContainerMetaclass

    _fields = list()
    _nullable_fields = set()
    _hashable_fields = set()
    _defaults = dict()

    def __init__(self, *args, **kwargs):
        # Assign defaults
        for k, v in self._defaults.iteritems():
            setattr(self, k, copy(v))

        # Assign positional arguments
        for field, value in zip(self._fields, args):
            setattr(self, field[0], copy(value))

        # Assign keyword arguments
        for field_name, value in kwargs.iteritems():
            setattr(self, field_name, copy(value))

    def update(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, copy(v))

    def serialize(self, io_file):
        """Serialize this instance into a IO like (file, StringIO...)."""
        for field in self._fields:
            f = getattr(self, field[0], None)
            if field[0] in self._nullable_fields:
                if f is None:
                    Bool().write(io_file, False)
                    continue
                else:
                    Bool().write(io_file, True)

            assert f is not None, "Field '{}' in class {} should not be None".format(
                field[0], self.__class__.__name__)
            field[1].write(io_file, f)

    @classmethod
    def deserialize(cls, io_file):
        """Deserialize the IO into a new instance."""
        ret = cls()
        try:
            for field in cls._fields:
                if field[0] in cls._nullable_fields:
                    if not Bool().read(io_file):
                        setattr(ret, field[0], None)
                        continue
                setattr(ret, field[0], field[1].read(io_file))
        except Exception as e:
            logger.error("Class %s failed with an exception on field %s",
                         cls.__name__, field[0])
            raise e
        else:
            return ret

    read = deserialize

    @classmethod
    def write(cls, io_file, value):
        assert isinstance(value, cls), \
            "Called `write` on class '%s' with an object of class '%s'" % (
            cls.__name__, type(value).__name__)
        value.serialize(io_file)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if not self._hashable_fields:
            return NotImplemented
        for field in self._hashable_fields:
            if getattr(self, field[0], None) != getattr(other, field[0], None):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        hash_val = 0
        hash_done = False
        if not self._hashable_fields:
            return NotImplemented
        for field in self._hashable_fields:
            field_value = getattr(self, field, None)
            if field_value is None:
                continue
            hash_done = True
            hash_val ^= hash(field_value)

        if not hash_done:
            raise TypeError("Could not find valid fields in order to perform hash")
        return hash_val

    def __repr__(self):
        if hasattr(self, "name"):
            return "<dataClay %s: %s>" % (self.__class__.__name__, self.name)
        else:
            return object.__repr__(self)

    def __str__(self):
        lines = list()

        lines.append("Container: %s" % self.__class__.__name__)
        for field_name, field_type in self._fields:
            lines.append("  - %s: %r" % (field_name, getattr(self, field_name)))

        return "\n".join(lines)
