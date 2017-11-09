# BOTLIB Framework to program bots
#
# botlib/cli.py
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

"""
    command line interfacce bot, gives a shell prompt to issue bot commands.

"""

from .static import BOLD, ENDC, RED
from .bot import Bot
from .event import Event

import sys

def init(*args, **kwargs):
    """ initialise a CLI bot, present prompt when done. """
    bot = CLI()
    bot.start()
    return bot

class CLI(Bot):

    """ Command Line Interface Bot. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompted = False
        self.register_fd(sys.stdin)
        self._threaded = True

    def dispatch(self, *args, **kwargs):
        from .space import kernel
        event = args[0]
        event.parse()
        kernel.prep(event)
        super().dispatch(event)
        self.prompt()

    def event(self):
        e = Event()
        e.cc = self.cc
        e.origin = "root@shell"
        e.server = "localhost"
        e.btype = self.type
        e.cb = "CLI"
        e.txt = input()
        self.prompted = False
        e.txt = e.txt.rstrip()
        return e

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        if self.prompted:
            return
        self.prompted = True
        sys.stdout.write("%s%s%s " % (BOLD, ">", ENDC))
        sys.stdout.flush()

    def raw(self, txt):
        """ output txt to sys.stdout """
        try:
            sys.stdout.write(txt)
        except TypeError:
            sys.stdout.write(str(txt))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def resume(self):
        from .space import kernel
        self._connected.clear()
        fn = os.path.join(cfg.workdir, "runtime", "fleet")
        logging.warn("# resume %s" % fn)
        f = Fleet().load(fn)
        for b in f:
            bot = compose(b)
            if not bot:
                continue
            id = bot.cfg.cfg + "." + bot.cfg.server
            if self.id() == id:
                fd = int(bot._resume.fd)
                if not fd:
                    self.announce("%s resume failed" % bot.cfg.server)
                    continue

    def start(self, *args, **kwargs):
        from .space import launcher
        super().start()
        self._connected.ready()
