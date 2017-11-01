# -*- coding: utf-8 -*-

"""
I/O routines.

io.py
(c) Will Roberts  23 June, 2017
"""

from __future__ import absolute_import

import codecs
import gzip
import sys
import zipfile
from collections import Counter

from .compat import basestring

try:
    import lzma
except ImportError:
    try:
        import backports.lzma as lzma
    except ImportError:
        pass


def open_file(filename, mode='rb'):
    """
    Open a file for access with the given mode.

    This function transparently wraps gzip and xz files as well as
    normal files.  You can also open zip files using syntax like::

        f = utils.open_file('../semcor-parsed.zip:semcor000.txt')

    :param str filename: The name of the file to open
    :param str mode: The mode to open the file in (defaults to 'rb')
    """
    if (('r' not in mode or hasattr(filename, 'read')) and
        (('a' not in mode and 'w' not in mode) or
         hasattr(filename, 'write')) and hasattr(filename, '__iter__')):
        return filename
    elif isinstance(filename, basestring):
        if filename == '-' and 'r' in mode:
            return sys.stdin
        elif filename == '-' and ('w' in mode or 'a' in mode):
            return sys.stdout
        if filename.lower().count('.zip:'):
            if 'r' not in mode:
                raise ValueError(
                    'zip file syntax only supports reading from files')
            mode = mode.replace('b', '')
            assert filename.count(':') == 1
            zipped_file = zipfile.ZipFile(filename.split(':')[0])
            unzipped_file = zipped_file.open(filename.split(':')[1], 'r')
            zipped_file.close()
            return unzipped_file
        elif filename.lower().endswith('.gz'):
            return gzip.open(filename, mode)
        elif filename.lower().endswith('.xz'):
            tmp = lzma.LZMAFile(filename, mode)
            dir(tmp)
            return tmp
        else:
            return open(filename, mode)
    else:
        raise TypeError('Unknown type for argument filename')


def lines(filename, encoding='utf-8'):
    """
    Open the named file and yield the lines inside it.

    :param str filename: The name of the file to open
    :param str encoding: The encoding of the file (defaults to utf-8)
    """
    with open_file(filename, 'rb') as input_file:
        if encoding is not None:
            stream = codecs.getreader(encoding)(input_file)
        else:
            stream = input_file
        for line in stream:
            yield line


def count_lines(filename):
    """
    Count the number of lines in the given text file.

    :param str filename:
    """
    num_lines = 0
    for _ in lines(filename, encoding=None):
        num_lines += 1
    return num_lines


def load_counter(filename, encoding='utf-8'):
    """
    Load a tab-separated count file into a Counter structure.

    The file contains zero or more lines, which begin with an integer
    count and follow with zero or more tab-separated string value
    fields in UTF-8 encoding.  This function stores these value fields
    in a tuple.

    The counts of repeated value lines will be summed together.

    :param str filename: The name of the file to open
    :param str encoding: The encoding of the file (defaults to utf-8)
    """
    counter = Counter()
    for line in lines(filename, encoding):
        line = line.strip().split('\t')
        cnt = int(line[0])
        value = tuple(line[1:])
        if len(value) == 1:
            counter[value[0]] += cnt
        else:
            counter[value] += cnt
    return counter
