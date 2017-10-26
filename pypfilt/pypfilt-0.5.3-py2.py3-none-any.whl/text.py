"""
Functions for ensuring consistent behaviour when using Python 2 or Python 3.

This is a much smaller module than existing cross-compatibility packages, such
as `python-future <http://python-future.org>`__ and
`six <https://pythonhosted.org/six/>`__.
"""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import sys

PY2 = sys.version_info[0] == 2


def to_unicode(value, encoding='utf-8'):
    """
    Convert a value into a Unicode string.

    + If the value is a Unicode string, no conversion is performed.
    + If the value is a byte string, it is decoded according to the provided
      encoding.
    + If the value is neither a Unicode string nor a byte string, it is
      first converted into a string (by the ``str()`` built-in function) and
      then decoded if necessary.
    """
    if PY2:
        if isinstance(value, unicode):
            return value
        elif isinstance(value, str):
            return value.decode(encoding)
        else:
            return to_unicode(str(value))
    else:
        if isinstance(value, str):
            return value
        elif isinstance(value, bytes):
            return value.decode(encoding)
        else:
            return str(value)


def to_bytes(value, encoding='utf-8'):
    """
    Convert a value into a byte string.

    + If the value is a Unicode string, it is encoded according to the
      provided encoding.
    + If the value is a byte string, no conversion is performed.
    + If the value is neither a Unicode string nor a byte string, it is
      first converted into a string (by the ``str()`` built-in function) and
      then encoded if necessary.
    """
    if PY2:
        if isinstance(value, unicode):
            return value.encode(encoding)
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    else:
        if isinstance(value, str):
            return value.encode(encoding)
        elif isinstance(value, bytes):
            return value
        else:
            return str(value).encode(encoding)


def is_unicode(value):
    """Return ``True`` if the value is a Unicode string."""
    if PY2:
        return isinstance(value, unicode)
    else:
        return isinstance(value, str)


def is_bytes(value):
    """Return ``True`` if the value is a byte string."""
    if PY2:
        return isinstance(value, str)
    else:
        return isinstance(value, bytes)
