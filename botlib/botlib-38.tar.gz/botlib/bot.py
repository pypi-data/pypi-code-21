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


""" bot base class. """

from .engine import Engine
from .error import ENOTIMPLEMENTED
from .object import Object
from .utils import sname

import logging
import queue
import time

class Bot(Engine):

    """ main bot class. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected = Object()
        self._outqueue = queue.Queue()
        self.channels = []
        self.cfg.fromdisk(self.type)

    def announce(self, txt):
        """ print text on joined channels. """
        if self.cfg.silent:
            return
        if not self.channels:
            self.direct(txt)
        for channel in self.channels:
            self.say(channel, txt)

    def direct(self, txt):
        """ output txt directly to bot. """
        pass

    def disconnect(self, e):
        """ disconnect from the server. """
        pass

    def disconnected(self):
        """ disconnected callback. """
        pass

    def id(self, *args, **kwargs):
        return sname(self).lower() + "." + (self.cfg.server or "localhost")

    def join(self, channel, password=""):
        """ join a channel. """
        pass

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def nick(self, nick):
        """ set bot's nick. """
        pass

    def out(self, channel, line):
        """ output text on channel. """
        self.say(channel, line)

    def raw(self, txt):
        """ send txt to server. """
        self._counter.raw += 1
        self.direct(txt)

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        pass

    def say(self, channel, txt, *args):
        """ say something on a channel. """
        if type(txt) in [list, tuple]:
            txt = ",".join(txt)
        self.raw(txt)

    def start(self, *args, **kwargs):
        from .space import fleet, launcher, runtime
        self._stopped = False
        fleet.add(self)
        super().start(*args, **kwargs)
