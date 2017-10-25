
# Compatability items for Python 3.2

import sys
from io import BytesIO

if sys.version_info < (3, 6):
    raise Exception('Kelvin requires Python 3.6 or later')

def toucs2(value):
    """
    Converts unicode objects to a bytes object encoded as UTF16-LE, which is the closest to a
    simple UCS2 Python has.
    """
    return value.encode('utf_16_le')


def tounicode(value):
    return value

def istext(value):
    return isinstance(value, str)

def isunicode(value):
    return isinstance(value, str)


def joinbytes(l):
    return b''.join(l)

padding = b'\0' * 3
