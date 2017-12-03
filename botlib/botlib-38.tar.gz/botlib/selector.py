# BOTLIB Framework to program bots
#
# botlib/selector.py
#
# Copyright 2017, 2018 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" functions used in code to select what objects to use. """

from .error import ENOTSET
from .register import Register

def selector(obj, keys):
    """ determine whether obj is part of the query. """
    if not keys:
        return True
    go = False
    for key in keys:
        try:
            attr = getattr(obj, key)
        except (AttributeError, ENOTSET):
            attr = None
        if attr != None:
            go = True
        else:
            go = False
            break
    return go

def wanted(obj, want):
    """ determine if the provided obj is matching criteria. """
    if not want:
        return True
    if list(want.keys()) == ["start"]:
        return True
    if list(want.keys()) == ["start", "end"]:
        return True
    go = False
    for key, values in want.items():
        if key in ["start", "end"]:
            continue
        value = getattr(obj, key, [])
        if not value:
            go = False
        for val in values:
            if val.startswith("-"):
                continue
            if val in value:
                go = True
            else:
                go = False
                break
        if not go:
            break
    return go

def notwanted(obj, notwant):
    """ determine whether this object in not wanted in a query. """
    if not notwant:
        return False
    for key in notwant:
        try:
            value = obj[key]
            return True
        except:
            pass
    return False

def ignore(obj, ign):
    """ check if object needs to be ignored. """
    if not ign:
        return False
    return False

def uniq(obj, uniqs, got_uniqs):
    """ see if this object is uniq. """
    if not uniqs:
        return False
    for key in uniqs:
        val = obj.get(key, None)
        if val and val not in got_uniqs.get(key, []):
            got_uniqs.register(key, val)
            return True
        else:
            return False
    return True
