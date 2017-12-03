# BOTLIB Framework to program bots
#
# botlib/clock.py
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

""" timer, repeater and other clock based classes. """

from .event import Event
from .object import Config, Object
from .utils import name

import os
import logging
import threading
import time

start = 0

def init(*args, **kwargs):
    """ initialise timers stored on disk. """
    timers = Timers()
    timers.start()
    return timers

class Timed(Event):

    """ Future Timer Object. """

    pass

class Timers(Object):

    """ run timers on their scheduled time. """

    def __init__(self, *args, **kwargs):
        self._stopped = False
        self.timers = Object()
        self._name = "Timers"
        for e in db.sequence("timed", self.cfg.latest):
            if e.done: continue
            if "time" not in e: continue
            if time.time() < int(e.time):
                self.timers[e.time] = e
        self.ready()

    def server(self):
        while not self._stopped:
            time.sleep(1.0)
            remove = []
            for t, event in self.timers.items():
                if time.time() > t:
                    event.direct(event.txt)
                    remove.append(t)
            for r in remove:
                del self.timers[r]
        
    def start(self):
        from .space import runtime
        launcher.launch(self.server)
        runtime["timers"] = self
        
    def stop(self):
        self._stopped = True

class Timer(Object):

    """ call a function as x seconds of sleep. """

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__()
        self.sleep = sleep
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._name = kwargs.get("name", name(self.func))
        try:
            self._event = self.args[0]
        except:
            self._event = Event()
        self._counter.run = 1

    def start(self):
        """ start the timer. """
        timer = threading.Timer(self.sleep, self.run, self.args, self.kwargs)
        timer.setName(self._name)
        timer.sleep = self.sleep
        timer._event = self._event
        timer._state = self._state
        timer._counter = self._counter
        timer._time = self._time
        timer._time.start = time.time()
        timer._time.latest = time.time()
        timer._state.status = "wait"
        timer.start()
        return timer

    def run(self):
        """ run the registered function. """
        self._time.latest = time.time()
        self.func(*self.args, **self.kwargs)

    def exit(self):
        """ cancel the timer. """
        self.cancel()

class Repeater(Timer):

    """ repeat an funcion every x seconds. """

    def run(self):
        self._counter.run = self._counter.run + 1
        self.func(*self.args, **self.kwargs)
        self.start()
