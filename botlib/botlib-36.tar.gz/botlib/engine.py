# BOTLIB Framework to program bots
#
# botlib/engine.py
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

""" select.epoll event loop, easily interrup_table esp. versus a blocking event loop. """

from .event import Event
from .error import ENOTIMPLEMENTED, EDISCONNECT
from .handler import Handler
from .object import Object
from .trace import get_exception
from .utils import sname

import logging
import select
import time

READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT
EDGE = select.EPOLLIN  | select.EPOLLOUT | select.EPOLLET

class Engine(Handler):

    """
        An engine is a front-end class to check for input and if ready ask the inherited class to construct an event based on this input.
        The created event is pushed to the base class (Handler) thats takes care of further event handling.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fds = []
        self._nrconnect = 0
        self._poll = select.epoll()
        self._resume = Object()
        self._state.status = "run"
        self._stopped = False
        self._time.start = time.time()

    def connect(self):
        """ connect to the server. """
        pass

    def error(self, *args, **kwargs):
        """ virtual error handler. """
        pass

    def event(self):
        """ virutal method to create an event, should be inherited. """
        raise ENOTIMPLEMENTED()

    def events(self):
        """ use poll to see if a bot is ready to receive input and if so, call the event() method to create an event from this input. """
        fdlist = self._poll.poll()
        for fd, event in fdlist:
            try:
                yield self.event()
            except Exception as ex:
                self.unregister_fd(fd)
                e = Event()
                e.command = e.cmnd = "ERROR"
                e.txt = str(type(ex)).lower()
                yield e

    def reconnect(self, event=None):
        """ run a connect loop until connected. """
        while 1:
            time.sleep(self._counter.connect * 5.0)
            try:
                self.connect()
                break
            except Exception as ex:
                logging.error(str(ex))

    def register_fd(self, fd):
        """ register filedescriptors to check for input. """
        try:
            fd = fd.fileno()
        except:
            pass
        if fd in self._fds:
            logging.warn("# fd %s already registered." % fd)
            return
        try:
            self._poll.register(fd)
        except:
            return fd
        self._fds.append(fd)
        logging.info("! engine on %s" % ",".join(str(x) for x in self._fds))
        return fd

    def resume(self):
        """ code to run when a engine has to be resumed. """
        logging.info("! resume on %s" % self._resume.fd)
        self._poll = select.epoll.fromfd(self._resume.fd)

    def select(self, *args, **kwargs):
        """ select loop defering the creation of events to the bot's class. """
        from .space import fleet, kernel, launcher
        while not self._stopped:
            for event in self.events():
                if event:
                    self.put(event)
                self._time.last = time.time()
        logging.info("! stop %s" % self._fds)
        fleet.remove(self)
        self._state.status = "stop"

    def start(self, *args, **kwargs):
        """ start the select() method in it's own thread. """
        from .space import launcher
        self._stopped = False
        launcher.launch(self.select)
        super().start()

    def stop(self):
        """ unregister all filedescriptors and close the polling object. """
        logging.info("! stop %s" % ",".join([str(x) for x in self._fds]))
        super().stop()
        for fd in self._fds:
            self.unregister_fd(fd)

    def unregister_fd(self, fd):
        """ remove a filedescriptor from the polling object. """
        if fd in self._fds:
            self._fds.remove(fd)
        try:
            self._poll.unregister(fd)
        except (PermissionError, FileNotFoundError):
            pass
