# BOTLIB Framework to program bots
#
# botlib/launcher.py
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

""" a launcher launches threads (or tasks in this case). """

from .event import Event
from .object import Object
from .task import Task
from .trace import get_from
from .utils import name as _name

import threading
import logging

class Launcher(Object):

    """ Laucher is able to launch a Task (see task.py). """

    cc = "!"

    def waiter(self, thrs, timeout=None):
        """ wait for tasks to finish. """
        result = []
        for thr in thrs:
            if not thr:
                continue
            try:
                res = thr.join(timeout)
                result.append(res)
            except AttributeError:
                pass
            except KeyboardInterrupt:
                break
        return result

    def launch(self, *args, **kwargs):
        """ launc a function with argument in it's own thread. """
        self._counter.launch += 1
        t = Task(**kwargs)
        t.start()
        t.put(*args, **kwargs)
        return t

    def kill(self, thrname=""):
        """ kill tasks matching the provided name. """
        thrs = []
        for thr in self.running(thrname):
            if thrname and thrname not in _name(thr):
                continue
            self._counter.killed += len(thrs)
            if "cancel" in dir(thr):
                thr.cancel()
            elif "exit" in dir(thr):
                thr.exit()
            elif "stop" in dir(thr):
                thr.stop()
            else:
                continue
            logging.info("! killed %s" % str(thr))
            thrs.append(thr)
        return thrs

    def running(self, tname=""):
        """ show what tasks are running. """
        for thr in threading.enumerate():
            if str(thr).startswith("<_"):
                continue
            yield thr
