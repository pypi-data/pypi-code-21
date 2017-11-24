# BOTLIB Framework to program bots
#
# botlib/trace.py
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

""" functions concering stack trace. """

import traceback
import sys
import os

stop = ["python3.5", "python3.6", "botlib"]

def get_exception(txt=""):
    """ return the exeption raced (one-lined markup). """
    from .space import cfg, exceptions
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for i in trace:
        fname = i[0]
        linenr = i[1]
        func = i[2]
        plugfile = fname[:-3].split(os.sep)
        mod = []
        for i in plugfile[::-1]:
            mod.append(i)
            if i == "botlib":
                break
        ownname = '.'.join(mod[::-1])
        result += "%s:%s %s | " % (ownname, linenr, func)
    del trace
    res = "%s%s: %s %s" % (result, exctype, excvalue, str(txt))
    if cfg.test:
        if res not in exceptions:
            exceptions.append(res)
    return res

def get_frame(depth=1, search="code"):
    """ get last frame of strack trace. """
    result = {}
    frame = sys._getframe(depth)
    search = str(search)
    for i in dir(frame):
        if search and search not in i:
            continue
        target = getattr(frame, i)
        for j in dir(target):
            result[j] = getattr(target, j)
    return result

def get_strace(depth=1):
    """ return stack trace. """
    result = ""
    loopframe = sys._getframe(depth)
    if not loopframe: return result
    while 1:
        try: frame = loopframe.f_back
        except AttributeError: break
        if not frame: break
        linenr = frame.f_lineno
        fn = frame.f_code.co_filename
        func = frame.f_code.co_name
        result += "%s %s:%s | " % (fn, func, linenr)
        loopframe = frame
    del loopframe
    return result[:-3]

def get_from(nr=2):
    """ return the plugin name where given frame occured. """
    frame = sys._getframe(nr)
    if not frame:
        return frame
    if not frame.f_back:
        return frame
    filename = frame.f_back.f_code.co_filename
    linenr = frame.f_back.f_lineno
    plugfile = filename.split(os.sep)
    del frame
    return ".".join(plugfile[-2:]) + ":" + str(linenr)
