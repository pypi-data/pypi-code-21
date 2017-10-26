"""

**serafin** is a serialization system that allows flexible serialization
of any type of object according to a provided fieldspec. The fieldspec tells
the serialize which attribute/fields/members of the given object should be
serialized. This allows for a very flexible serialization system, especially in
the context of API endpoints where we can write one endpoint and allow client
to pass the fieldspec describing how he wants the output to be formatted.


.. autoclass:: serafin.core.Priority
    :members:


.. autoclass:: serafin.core.Serializer
    :members:


.. autofunction:: serafin.core.serialize

"""
from .core import Priority, serializer, serialize
from .core_serializers import *     # pylint: disable=wildcard-import
from .fieldspec import Fieldspec
__all__ = [
    'Priority',
    'serializer',
    'serialize',
    'Fieldspec',
]
