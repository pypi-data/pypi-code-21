# BOTLIB Framework to program bots
#
# botlib/kernel.py
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

""" program boot and module loading. """

from .decorator import locked, space
from .engine import Engine
from .event import Event
from .launcher import Launcher
from .log import loglevel
from .object import Config, Object
from .raw import RAW
from .register import Register
from .static import BOLD, ENDC, GRAY
from .trace import get_exception
from .utils import cdir, set_completer, stripped

import logging
import os
import sys
import time

class ModuleNotFoundError(ImportError):
    pass

class Kernel(Engine, Launcher):

    """
        Kernel object does the startup/shutdown of the bot.
        Call Kernel.boot() at the start of your program.

    """

    def announce(self, txt, full=False):
        """ announce txt on all fleet bot. """
        from .space import fleet
        for bot in fleet:
            bot.announce(txt)

    def boot(self, cfgin):
        """ start the kernel. """
        from .space import cfg, fleet, launcher, load, reserved, users
        dosave = False
        self._time.start = time.time()
        cfg.update(cfgin)
        if cfg.user:
            cfg.uber = True
            cfg.shell = True
            cfg.banner = True
            cfg.verbose = True
            cfg.loglevel = cfg.loglevel or "warn"
        else:
            cfg.loglevel = cfg.loglevel or "error"
        loglevel(cfg.loglevel)
        if cfg.banner:
            print("%s%s%s #%s Framework to program bots%s\n" % (BOLD, GRAY, cfg.name.upper(), cfg.version, ENDC))
        if cfg.license:
            from botlib import __license__
            print(__license__)
            print()
        if cfg.test:
            cfg.logdir = "botlog"
            cfg.workdir = "data"
            cfg.changed = True
            cfg.verbose = True
        if not cfg.test and cfg.loglevel in ["debug", "info", "warn"]:
            cfg.verbose = True
        if not cfg.workdir:
            cfg.workdir = os.path.join(cfg.homedir, ".bot")
        logging.info("# workdir %s" % cfg.workdir)
        logging.info("# loglevel %s" % cfg.loglevel)
        if not os.path.exists(cfg.workdir):
            cdir(cfg.workdir)
        users.uber("root@shell")
        if cfg.test:
            cfg.user = True
            users.uber("test@shell")
            users.delete("test@shell", "MBOX")
            users.delete("test@shell", "EXIT")
        if cfg.eggs:
            self.load_eggs()
        if not self._names:
            p = os.path.join(cfg.workdir, "runtime", "kernel")
            try:
                k = Object().load(p)
                if "_names" in k:
                    self._names.update(k._names)
            except ValueError:
                pass
        if not self._names or cfg.write:
            self._names = Register()
            self.walk("botlib", True)
            cfg.write = True
        load()
        self.start()
        try:
            sys.path.insert(0, cfg.homedir)
            self.walk("botmods")
        except ImportError:
            pass
        except ModuleNotFoundError:
            pass
        except:
            logging.error(get_exception())
        for modname in cfg.mods.split(","):
            if modname:
                try:
                    self.walk(modname)
                except Exception as ex:
                    logging.error(str(ex))
        for modname in cfg.needed:
            self.init(modname)
        loglevel(cfg.loglevel)
        if cfg.all or cfg.init:
            cfg.shell = True
            thrs = []
            for pname in cfg.packages:
                for modname in self.modules(pname):
                    n = modname.split(".")[-1]
                    if n in cfg.exclude.split(","):
                        continue
                    if modname in cfg.needed or (modname in cfg.ignore and n not in cfg.init):
                        continue
                    if cfg.all or n in cfg.init.split(","):
                        thr = self.init(modname)
                        if thr:
                            thrs.append(thr)
            for thr in thrs:
                thr.join()
        if cfg.write:
            self.sync(os.path.join(cfg.workdir, "runtime", "kernel"))
        if not self._cmnds:
            self._cmnds = sorted(set([cmnd for cmnd in self._names.keys()]))
        set_completer(self._cmnds)
        if cfg.shell:
            for bot in fleet:
                bot.prompt()
                bot.wait()
            mod = self.init("botlib.cli")
            self.shell = mod.join()
            self.shell.prompt()
            self.shell.wait()
        elif cfg.args:
            e = self.once(" ".join(cfg.args))
            e.wait()
        self.ready()
        return self

    def cmnd(self, txt):
        """ execute a command based on txt. """
        from .space import cfg, fleet
        cfg.shell = False
        bot = RAW()
        fleet.add(bot)
        event = Event()
        event.id = bot.id()
        event.cc = ""
        event.origin = "root@shell"
        event.channel = "#botlib"
        event.server = "localhost"
        event.btype = bot.type
        event.txt = txt
        return event

    def event(self, cmnd):
        """ return an event for <cmnd>. """
        e = Event()
        e.txt = cmnd
        self.prep()
        return e
 
    def init(self, modname):
        """ initialize a module. """
        from .space import launcher
        event = Event()
        n = modname.split(".")[-1]
        mod = self._table.get(modname, None)
        if not mod or type(mod) == str:
            mod = self.load(modname, True)
        if mod and "init" in dir(mod):
            logging.info("! init %s" % modname)
            thr = launcher.launch(mod.init, event, name="init %s" % modname)
            return thr

    def load_config(self):
        """ load cfg from file. """
        from .space import cfg
        c = Config().load(os.path.join(cfg.workdir, "runtime", "cfg"))
        cfg.update(c)

    def load_eggs(self):
        """ load eggs from current directory. """
        from .space import cfg
        for fn in os.listdir(os.getcwd()):
            if fn.endswith(".egg"):
                if cfg.verbose:
                    logging.info("! egg %s" % fn)
                sys.path.insert(0, fn)

    def once(self, txt):
        """ run once command. """
        e = self.cmnd(txt)
        e.verbose = True
        self.put(e)
        e.wait()
        return e

    def register(self, key, val):
        logging.warn("# register %s %s" % (key, name(val)))
        return super().register(key, val)

    def reload(self, name, force=True, event=None):
        """ reload module. """
        e = event or Event()
        if name not in self._table:
            return
        if "shutdown" in dir(self._table[name]):
            self._table[name].shutdown(e)
        self.load(name, force)
        if force:
            self._table[name].init(e)
        if name in self._table:
            return self._table[name]

    @locked
    def shutdown(self, close=False, write=False):
        """ stop bot, services and plugins. """
        from .space import cfg, events, exceptions, launcher, pool, runner, save
        logging.info("! shutdown")
        logging.info("")
        save()
        if cfg.write:
            cfg.save()
            fleet.save()
        event = Event()
        event.txt = "shutdown"
        event.server = "kernel"
        thrs = []
        if close:
            for key, mod in self._table.items():
                logging.warn("# shutdown %s" % key)
                try:
                    mod.shutdown(event)
                except AttributeError:
                    continue
                except:
                    logging.error(get_exception())
        if cfg.test:
            for ex in exceptions:
                print(ex)
        sys.stdout.flush()
        self.ready()
