#  -*- coding: utf-8 -*-
# *****************************************************************************
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import numpy


def string(s=None):
    """a string"""
    if s is None:
        return ''
    try:
        return str(s)
    except UnicodeError:
        # on Python 2, this converts Unicode to our preferred encoding
        if isinstance(s, str):
            return s.encode('utf-8')
        raise


def convdoc(conv):
    if isinstance(conv, type):
        return conv.__name__
    return conv.__doc__ or ''


def fixup_conv(conv):
    """Fix-up a single converter type.

    Currently this converts "str" to "string" which is a version that supports
    Unicode strings by encoding to str on Python 2.
    """
    if conv is str:
        return string
    return conv


class dictof(object):
    def __init__(self, keyconv, valconv):
        self.__doc__ = 'a dict of %s keys and %s values' % \
                       (convdoc(keyconv), convdoc(valconv))
        self.keyconv = fixup_conv(keyconv)
        self.valconv = fixup_conv(valconv)

    def __call__(self, val=None):
        val = val if val is not None else {}
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in val.items():
            ret[self.keyconv(k)] = self.valconv(v)
        return ret


class listof(object):
    def __init__(self, conv):
        self.__doc__ = 'a list of %s' % convdoc(conv)
        if conv is str:
            conv = string
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        val = val if val is not None else []
        if not isinstance(val, (list, tuple)):
            raise ValueError('value needs to be a list')
        return list(map(self.conv, val))


class oneof(object):
    def __init__(self, *vals):
        self.__doc__ = 'one of ' + ', '.join(map(repr, vals))
        self.vals = vals

    def __call__(self, val=None):
        if val is None:
            if self.vals:
                return self.vals[0]
            return None
        if val not in self.vals:
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, self.vals))))
        return val


class dictwith(object):
    def __init__(self, **convs):
        self.__doc__ = 'a dict with the following keys: ' + \
            ', '.join('%s: %s' % (k, convdoc(c)) for k, c in convs.items())
        self.keys = set(convs)
        self.convs = convs

    def __call__(self, val=None):
        if val is None:
            return dict((k, conv()) for k, conv in self.convs.items())
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        vkeys = set(val)
        msgs = []
        if vkeys - self.keys:
            msgs.append('unknown keys: %s' % (vkeys - self.keys))
        if self.keys - vkeys:
            msgs.append('missing keys: %s' % (self.keys - vkeys))
        if msgs:
            raise ValueError('Key mismatch in dictionary: ' + ', '.join(msgs))
        ret = {}
        for k in self.keys:
            ret[k] = self.convs[k](val[k])
        return ret


class numpyarray(object):
    def __init__(self, shape=None, datatype=None):
        self._shape = shape
        self._datatype = datatype

        self.__doc__ = 'a numpy array of %s with shape %r' % (datatype, shape)

    def __call__(self, val):
        ret = numpy.asarray(val, dtype=self._datatype)

        if self._shape:
            ret.shape = self._shape

        return ret


def anytype(val=None):
    """any value"""
    return val
