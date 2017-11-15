# coding=utf-8

"""
Handle string to bytes conversion for python 2 & 3.

From: http://python3porting.com/problems.html#bytes-strings-and-unicode

Usage
-----

::

    from fullmonty.make_bytes import b

    with open(file_name, 'w') as file_:
        file_.write(b(str_variable))

"""

import sys
if sys.version < '3':
    # noinspection PyDocstring
    def b(x):
        return x
else:
    import codecs

    # noinspection PyDocstring
    def b(x):
        return codecs.latin_1_encode(x)[0]
