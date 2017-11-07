import sys


PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode
    string_classes = (str, unicode)
else:
    text_type = str
    string_classes = (str, bytes)


def to_bytes(x):
    if isinstance(x, text_type):
        return x.encode('utf-8')
    if not isinstance(x, bytes):
        raise TypeError('Bytes or string expected')

    return x


def a_string(s):
    return isinstance(s, string_classes)
