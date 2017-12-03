# BOTLIB Framework to program bots
#
# botlib/runner.py
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

""" threaded loop to run tasks on. """

from .task import Task
from .trace import get_exception
from .utils import name

import logging
import time

class Runner(Task):

    """ while loop handling events placed in a thread (should mimic a logical CPU). """

    def run(self):
        """ run a loop that handles jobs. """
        from .space import profiler
        self._running = True
        self._stopped = False
        self._event = None
        self.setName(self._name)
        while not self._stopped:
            func, args, kwargs = self._queue.get()
            if self._stopped:
                break
            time.sleep(0.001)
            self._busy = True
            if args and type(args[0]) == Event:
                self._event = args[0]
                self._error.cmnd = self._event._parsed.cmnd
            self._counter.run += 1
            self._begin = time.time()
            self._state.status = "run"
            try:
                result = func(*args, **kwargs)
            except Exception as ex:
                logging.error("%s: %s" % (str(func), get_exception()))
            self._end = time.time()
            self._elapsed = self._begin - self._end
            if self._elapsed > 5.0:
                profiler[self._error.cmnd] = self._elapsed
            self._busy = False
            self._state.status = "idle"
            self._event = None
        self._state.status = "stopped"
