# BOTLIB Framework to program bots
#
# botlib/task.py
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

""" adapted thread to add extra functionality to threads. """

from .object import Default, Object
from .event import Event
from .trace import get_exception
from .utils import name as _name

import logging
import queue
import threading
import time

class Task(threading.Thread):

    """ Task are adapted Threads. """

    def __init__(self, *args, **kwargs):
        super().__init__(None, self.run, "", [], {}, daemon=False)
        n = kwargs.get("name", None)
        if n:
            self.setName(n)
        self._connected = Object()
        self._counter = Default(default=0)
        self._error = Default()
        self._ready = threading.Event()
        self._queue = queue.Queue()
        self._result = 0
        self._name = kwargs.get("name", self.name)
        self._state = Default()
        self._time = Default(default=0)
        self._time.start = time.time()

    def __iter__(self):
        """ return self as an iterator. """
        return self

    def __next__(self):
        """ yield next value. """
        for k in dir(self):
            yield k

    def put(self, *args, **kwargs):
        """ send an event to the task. """
        self._queue.put_nowait((args[0], args[1:], kwargs))

    def run(self):
        """ take an event from the queue and proces it. """
        (func, args, kwargs) = self._queue.get()
        self._counter.size = self._queue.qsize()
        self._event = None
        if args and type(args[0]) in [Event,]:
            self._event = args[0]
            try:
                self._event.parse()
                n = self._event._parsed.cmnd
                if n:
                    self._name = n
                else:
                    n = _name(self._event.txt)
            except:
                pass
        else:
            n = _name(func)
            self.setName(n)
        self._state.status = "run"
        try:
            self._result = func(*args, **kwargs)
        except Exception as ex:
            logging.error("%s: %s" % (str(func), get_exception()))
            self._error.msg = str(ex)
            self.ready()
        self._state.status = "idle"
        return self._result or 0

    def isSet(self):
        """ see if the object ready flag is set. """
        return self._ready.isSet()

    def join(self, sleep=None):
        """ join this task and return the result. """
        super().join(sleep)
        return self._result or 0

    def ready(self):
        """ signal the event as being ready. """
        self._ready.set()

    def clear(self):
        """ clear the ready flag. """
        self._ready.clear()

    def wait(self, sec=180.0):
        """ wait for the task to be ready. """
        self._ready.wait(sec)
        return self._result
 