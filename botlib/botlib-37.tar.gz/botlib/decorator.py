# BOTLIB Framework to program bots
#
# botlib/decorator.py
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

""" method decorators. """

import functools
import _thread

def space(func, *args, **kwargs):

    """ import space variable into function's global space. """

    @functools.wraps(func)
    def f(*args, **kwargs):
        f.__name = func.__name__
        from .object import Object
        import botlib.space

        params = Object(**kwargs)
        nrvar = func.__code__.co_argcount
        varnames = func.__code__.co_varnames
        for x in range(len(args)):
            params[varnames[x]] = args[x]
        func.__globals__["params"] = params
        for name in botlib.space.__all__:
            if name not in dir(func.__globals__):
                func.__globals__[name] = getattr(botlib.space, name)
        return func(*args, **kwargs)

    return f

def locked(func, *args, **kwargs):
    """ locked decorator. """

    lock = _thread.allocate_lock()

    @functools.wraps(func)
    def lockedfunc(*args, **kwargs):
        """ lockde function wrapper to be return as the decorator. """
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc
