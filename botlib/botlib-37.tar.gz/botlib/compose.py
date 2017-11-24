# BOTLIB Framework to program bots
#
# botlib/bot.py
#
# Copyright 2017 B.H.J Thate
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

""" construct a object into it's type. """

import sys

def compose(o, self=None):
    """ reconstruct an typed Object from json file. """
    from .object import Object
    if not o:
        return o
    t = type(o)
    if t in [None, bool, True, False, int, float]:
        return o
    if t in [str,]:
        ot = from_string(o)
        try:
            return ot()
        except:
            return o
    if t in [list, tuple]:
        l = []
        for item in o:
            l.append(compose(item))
        return l
    try:
        ts = o["_type"]
        t = from_string(ts)
    except (TypeError, KeyError):
        t = Object
    if not t or not "items" in dir(o):
        return t
    oo = t()
    for k, v in o.items():
        if k == "_type":
            continue
        oo[k] = compose(v)
    return oo

def from_string(s):
    """ given a str(obj) return the object constructed. """
    from .space import kernel
    bs = s
    if s.startswith("<class"):
        s = s.split()[-1][1:-2]
    elif s.startswith("<function"):
        funcname = s.split()[1]
        try:
            return globals()[funcname]
        except:
            return None
    elif s.startswith("<module"):
        s = s.split()[1]
    elif "object" in s:
        s = s.split()[0][1:].strip()
    try:
        m, c = s.rsplit(".", 1)
    except:
        try:
            m = s.split(".")[-1]
            c = ""
        except:
            return None
    if not m:
        return None
    if "botlib.utils" in m:
        mod = m
    else:
        try:
            mod = sys.modules[m]
        except KeyError:
            if m in kernel._table:
                mod = kernel.direct(m)
                return mod
            else:
                return None
    o = getattr(mod, c, None)
    return o
