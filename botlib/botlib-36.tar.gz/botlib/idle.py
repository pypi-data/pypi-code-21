# BOTLIB Framework to program bots
#
# botlib/idle.py
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

from .object import Object
from .utils import elapsed

import time
import os

idle = Object()

def init(*args, **kwargs):
    runtime["idle"] = Object()
    runtime["idle"].load(os.path.join(cfg.workdir, "runtime", "idle"))

def shutdown(*args, **kwargs):
    """ save idle data to runtime directory. """
    runtime["idle"].save(os.path.join(cfg.workdir, "runtime", "idle"))

def idle_cb(event):
    if not runtime.get("idle", None):
        runtime["idle"] = Object()
    runtime["idle"][event.origin] = time.time()
    runtime["idle"][event.channel] = time.time()

idle_cb.cbs = ["PRIVMSG", "CLI"]

def idle(event):
    """ see how long a channel/nick has been idle. """
    origin = event._parsed.rest
    if not origin:
        origin = event.channel
    else:
        origin = fleet.get_origin(origin)
    if not runtime.get("idle", None):
        runtime["idle"] = Object()
    if origin in runtime["idle"]:
        event.reply("%s is idle for %s" % (origin, elapsed(time.time() - runtime["idle"][origin])))
    else:
        event.reply("haven't seen %s" % origin)
