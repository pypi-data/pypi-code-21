# BOTLIB Framework to program bots
#
# botlib/handler.py
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

""" schedule events. """

from .decorator import locked
from .error import ENOWORKER, ENOCOMMAND
from .object import Default, Object
from .register import Register
from .trace import get_exception, get_from
from .utils import elapsed, name

import importlib
import logging
import pkgutil
import queue
import time
import types

class Handler(Object):

    """
        A Handler handles events pushed to it. Handlers can be threaded,
        e.g. start a thread on every event received, or not threaded in which
        case the event is handeled in loop.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._booted = Object()
        self._cbs = Register()
        self._cmnds = []
        self._descriptions = Object()
        self._handlers = Register()
        self._names = Register()
        self._queue = queue.Queue()
        self._running = False
        self._stopped = False
        self._threaded = False
        self._finished = Object()
        self._handlers = Register()
        self._names = Register()
        self._scanned = False
        self._stopped = False
        self._table = Object()
        self._time = Default(default=0)

    def direct(self, name, package=None, log=False):
        """ import a module directly, not storing it in the cache. """
        import botlib.space
        log and logging.warn("# direct %s" % name)
        mod = importlib.import_module(name, package)
        for name in botlib.space.__all__:
            if name not in dir(mod):
                setattr(mod, name, getattr(botlib.space, name))
            else:
                setattr(mod, "_" + name, getattr(botlib.space, name))
        return mod

    def dispatch(self, *args, **kwargs):
        """ handle an event. """
        from .space import cfg, users
        event = args[0]
        if not event.txt:
            event.ready()
            return event
        event.parse()
        if not event._funcs and not event._cbs:
            event.ready()
            return event
        logging.info("! dispatch %s %s %s" % (event.origin, " ".join([name(x).strip() for x in event._funcs]), " ".join([name(x).strip() for x in event._cbs])))
        starttime = time.time()
        for cb in event._cbs:
            try:
                 cb(event)
            except:
                 logging.error(get_exception())
        if not cfg.kill:
            for func in event._funcs:
                if "perm" in dir(func):
                    if not users.allowed(event.origin, func.perm):
                        event._denied = func.perm
                        event.ready()
                        return event
        try:
            event.dispatch()
        except:
            logging.error(get_exception())
        if event.batch:
            event.show()
        logging.info("! finished in %s seconds" % elapsed(time.time() - starttime))
        event.ready()
        return event

    def errored(self, event):
        """ error handler. """
        pass

    def get_cbs(self, cmnd):
        cbs = self._cbs.get(cmnd, [])
        all = self._cbs.get("ALL", [])
        cbs.extend(all)
        return cbs

    def get_handlers(self, cmnd):
        """ search for a function registered by command. """
        from botlib.space import alias
        oldcmnd = cmnd
        cmnd = alias.get(cmnd, cmnd)
        if cmnd not in self._handlers:
            for modname in self._names.get(cmnd, []):
                self.load(modname, force=True, log=True)
        funcs = self._handlers.get(cmnd, [])
        if not funcs:
            funcs = self._handlers.get(oldcmnd, [])
        return funcs

    def list(self, name):
        """ list all functions found in a module. """
        for modname in self.modules(name):
            mod = self.load(modname)
            for key in dir(mod):
                if key in ["init", "shutdown"]:
                    continue
                obj = getattr(mod, key, None)
                if obj and type(obj) == types.FunctionType:
                    if "event" in obj.__code__.co_varnames:
                        yield key

    @locked
    def load(self, modname, force=False, log=False):
        """ load a module. """
        if force or modname not in self._table:
            self._table[modname] = self.direct(modname, log=log)
        elif modname in self._table:
            return self._table[modname]
        for key in dir(self._table[modname]):
            if key.startswith("_"):
                continue
            obj = getattr(self._table[modname], key, None)
            if obj and type(obj) == types.FunctionType:
                if "__wrapped__" in dir(obj):
                    func = obj.__wrapped__
                else:
                    func = obj
                if key.endswith("_cb"):
                    try:
                        cbs = func.cbs
                    except:
                        continue
                    for cb in cbs:
                        self._cbs.register(cb, func)
                        #self._names.register(cb, modname)
                if "event" in func.__code__.co_varnames:
                    self._names.register(key, modname)
                    if key not in ["init", "shutdown"]:
                        self._handlers.register(key, obj)
                        if "__doc__" in dir(obj):
                            self._descriptions.register(key, obj.__doc__, True)
        return self._table[modname]

    def modules(self, name):
        """ return a list of modules in the named packages or cfg.packages if no module name is provided. """
        package = self.load(name)
        for pkg in pkgutil.walk_packages(package.__path__, name + "."):
            yield pkg[1]

    def prep(self, event):
        event._cbs = self.get_cbs(event.cb)
        event._funcs = self.get_handlers(event._parsed.command or event._parsed.cmnd)
        for func in event._funcs:
            if "_threaded" in dir(func) and func._threaded:
                event._threaded = True
                break

    def scheduler(self):
        """ main loop of the Handler. """
        from .space import launcher, pool, runner
        self._state.status = "run"
        self._time.latest = time.time()
        while not self._stopped:
            self._counter.nr += 1
            self._state.status = "wait"
            args, kwargs = self._queue.get()
            if not args:
                self._stopped = True
                break
            event = args[0]
            if not event:
                break
            if event.pooled:
                try:
                    pool.put(self.dispatch, event)
                except ENOWORKER:
                    thr = launcher.launch(self.dispatch, event)
                    event._thrs.append(thr)
                except Exception as ex:
                    event.direct(get_exception())
                    event.ready()
                    event.prompt()
            else:
                thr = launcher.launch(self.dispatch, event)
                event._thrs.append(thr)
        self._state.status = "done"

    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        self._queue.put_nowait((args, kwargs))

    def register(self, key, val, force=False):
        """ register a handler. """
        logging.info("! register %s.%s" % (key, name(val)))
        self._handlers.register(key, val, force=force)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        from .space import launcher
        self._stopped = False
        launcher.launch(self.scheduler)

    def stop(self):
        """ stop the handler. """
        self._stopped = True
        self._state.status = "stop"
        self._queue.put((None, None))

    def walk(self, name, init=False, force=False, log=False):
        """ return all modules in a package. """
        self._scanned = True
        for modname in sorted(list(self.modules(name))):
            self.load(modname, force, log)
