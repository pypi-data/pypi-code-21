
# Compatability items for Python 2.7

import sys
from cStringIO import StringIO as BytesIO

# Python 2.7 support is temporary right now.  There is no optimize keyword to the compile
# function.
if sys.version_info < (2, 7):
    raise Exception('Kelvin requires Python 2.7 or later')

def toucs2(value):
    """
    Converts str or unicode objects to a byte array encoded as UTF16-LE, which is the closest
    to a simple UCS2 Python has.
    """
    if type(value) is str:
        value = unicode(value) # , 'unicode_escape')
    return value.encode('utf_16_le')


def tounicode(value):
    if type(value) is str:
        value = unicode(value) # , 'unicode_escape')
    return value
    
def istext(value):
    return isinstance(value, (str, unicode))

def isunicode(value):
    return isinstance(value, unicode)

def joinbytes(l):
    return ''.join(l)

padding = '\0' * 3
