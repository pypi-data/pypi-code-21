# BOTLIB Framework to program bots
#
# botlib/watcher.py
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

""" watch files. """

from .object import Object
from .space import cfg, db, launcher
from .trace import get_exception

import logging
import select
import time
import os

def init(*args, **kwargs):
    """ initialize a watcher server. """
    watcher = Watcher()
    watcher.start()
    return watcher

def out(txt):
    """ output function. """
    print(txt)

class Watcher(Object):

    """ Register filename to watch with the !watch <fm> command. """

    def start(self):
        """ start file watcher. """
        launcher.launch(self.server)

    def server(self):
        """ server function of the watcher. """
        watchers = []
        for fn in self.watchlist():
            try:
                reader = open(fn, "r")
                reader.seek(0, 2)
                fd = reader.fileno()
                watchers.append(fd)
            except FileNotFoundError as ex:
                logging.info("! not watching %s" % fn)
        if not watchers:
            logging.info("! no watchers found.")
            self.ready()
            return
        self._state.status = "run"
        self.ready()
        while 1:
            time.sleep(1.0)
            (i, o, e) = select.select(watchers, [], [])
            for fd in i:
                try:
                    txt = os.read(fd, 1024)
                    out(txt)
                except:
                    logging.error(get_exception())
        self._state.status = "stop"

    def watchlist(self):
        """ return a list of filenames to watch. """
        w = list([x.watch for x in db.find("watch")])
        if cfg.watch:
            w.append(cfg.watch)
        return w
