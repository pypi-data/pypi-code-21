"""Management of primitives types.

The management of basic primitive types inside the dataClay is done in this
submodule. Keeping in mind the endianness transmission over the network, its
architecture dependant size, etc.

This submodule offers basic classes for all dataClay primitive types (regarding
internal serialization).
"""

from _basic import *
from _non_basic import *


__all__ = ["Serializable", "PrimitiveType", "Int", "Vlq",
           "Float", "Str", "Bool", "DCID", "Dict", "Null", "PyTypeWildcard",
           "IfaceBitMaps", "BitMap", "List", "Set", "Calendar",
           "Tuple", "NotImplementedType"]
