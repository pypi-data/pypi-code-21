# BOTLIB Framework to program bots
#
# botlib/db.py
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

""" JSON file backed object with dotted access.  """

from .decorator import locked
from .error import ENOJSON, EBORDER
from .utils import smooth, sname, make_signature, get_path, rtime, cdir, verify_signature, urled, name

import botlib
import fcntl
import json
import logging
import os
import time
import threading
import _thread

def locked(func, *args, **kwargs):
    """ locked decorator, use to lock decorator function. """

    lock = _thread.allocate_lock()

    def lockedfunc(*args, **kwargs):
        """ lockded function to wrap a function in. """
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc

class Object(dict):

    """
        Dict with dotted access instead of brackets, with json files to sync and load from.

    """

    def __getattribute__(self, name):
        """ get attribute and if fail check item access. """
        if name == "_path":
            from botlib.space import cfg
            p = os.path.join(cfg.workdir, sname(self).lower())
            return p
        if name == "url":
            return urled(self)
        if name == "_type":
            return str(type(self))
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

    def __getattr__(self, name):
        """
            Get missing attribute by name. initialize into an Object if if name is missing from dictionary.
            Predefined names are _ready and counter. _ready is for waiting on results and counter is for integer simulation.

        """
        if name == "_connected":
            self._connected = Object()
        if name == "_container":
            self._container = Default()
        if name == "_counter":
            self._counter = Default(default=0)
        if name == "_error":
            self._error = Default()
        if name == "_finished":
            self._finished = False
        if name == "_fixed":
            self._fixed = ""
        if name == "_funcs":
            self._funcs = []
        if name == "_ready":
            self._ready = threading.Event()
        if name == "_state":
            self._state = Object()
        if name == "_status":
            self._status = Object()
        if name == "_thrs":
            self._thrs = []
        if name == "_time":
            self._time = Default(default=0.0)
        if name == "type":
            return sname(self).lower()
        if name == "cfg":
            self.cfg = Config().template(sname(self).lower())
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        """ return module.class as a class type. """
        return '<%s.%s at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def __setattr__(self, name, value):
        """ implement dotted dict access. """
        return self.__setitem__(name, value)

    def __str__(self):
        """ return a prettified json string. """
        return self.nice()

    def grep(self, val):
        """ grep for a matching stringified value, return a Object with those matching values. """
        o = Object()
        for key, value in self.items():
            if val in str(value) and value not in o:
                o[key] = value
        return o

    def id(self):
        """ return lowered class name as the type. """
        return sname(self).lower()

    def cache(self, path):
        from .space import cache
        if path in cache:
            return cache[path]
        return self.load(path)

    def load(self, path, force=False, skip=[], full=True):
        """ load a json file into this object. use skip as a list of keys to skip. """
        from .space import cache, cfg
        from .error import EBORDER
        path = os.path.abspath(path)
        if not cfg.workdir in path:
            raise EBORDER(path)
        logging.debug("! load %s" % os.sep.join(path.split(os.sep)[-3:]))
        ondisk = self.read(path)
        self._container.path = path
        fromdisk = json.loads(ondisk)
        if "signature" in fromdisk:
            if not verify_signature(fromdisk["data"], fromdisk["signature"]) and not force:
                logging.warn("# mismatch %s" % os.sep.join(path.split(os.sep)[-3:]))
        if "data" in fromdisk:
            self.update(slice(fromdisk["data"], skip=skip, full=full))
            self._container.update(slice(fromdisk, skip=["data"]))
        cache[path] = self
        return self

    def loads(self, s):
        """ update with deconstructed (dict) json string. """
        self.update(json.loads(s))

    def merge(self, obj):
        """ merge an object into this on, only set keys that are already present. """
        for k, v in obj.items():
            if v:
                self[k] = v

    @locked
    def nice(self, *args, **kwargs):
        """ return a nicyfied, indent=4, sort_key is True, json dump. """
        return json.dumps(self, default=smooth, indent=4, sort_keys=True)

    def pure(self, *args, **kwargs):
        """ return a sliced (no _ keys), indent=4, sort_key is True, json dump. """
        return json.dumps(slice(self, full=False), indent=4, sort_keys=True)

    def prepare(self):
        """
            prepare the object and return a string containing the "data" part.
            keyword can be "prefix" when using a subdirectory.
            use "saved" when savestamp need to be different from the "now" timestamp.

        """
        todisk = Object()
        todisk.data = dumped(slice(self, skip=["_container", "_parsed"], full=True))
        todisk.data._type = str(type(self))
        if "prefix" not in todisk:
            todisk.prefix = sname(self).lower()
        todisk.saved = time.ctime(time.time())
        try:
            todisk.signature = make_signature(todisk["data"])
        except:
            pass
        try:
            result = json.dumps(todisk, default=smooth, indent=4, ensure_ascii=False, sort_keys=True)
        except TypeError:
            raise ENOJSON
        return result

    def printable(self, keys=[], skip=[], nokeys=False, reverse=False):
        """ determine from provided keys list and/or from skipping from a skiplist a displayable string from those attributes. """
        keys = keys or self.keys()
        if reverse:
            keys = reversed(list(keys))
        result = []
        for key in reversed(list(keys)):
            if key == "default":
                continue
            if key.startswith("_"):
                continue
            if key in skip:
                continue
            if nokeys:
                result.append("%-8s" % str(self[key]))
            else:
                result.append("%10s" % "%s=%s" % (key, str(self[key])))
        txt = " ".join(result)
        return txt.rstrip()

    def read(self, path):
        """ read a json dump from given path, returning the json string with comments stripped. """
        try:
            f = open(path, "r", encoding="utf-8")
        except FileNotFoundError:
            return "{}"
        res = ""
        for line in f:
            if not line.strip().startswith("#"):
                res += line
        if not res.strip():
            return "{}"
        f.close()
        return res

    def register(self, key, val, force=False):
        """ register key, value and throw an exception is value is already set. """
        if key in self and not force:
            raise botlib.error.ESET(key)
        self[key] = val

    @locked
    def save(self, *args, **kwargs):
        """ save a static (fix filepath) version of this object. """
        return self.sync(*args, **kwargs)

    def search(self, name):
        """ search this objects keys skipping keys that start with "_". """
        o = Object()
        for key, value in self.items():
            if key.startswith("_"):
                continue
            if key in name:
                o[key] = value
            elif name in key.split(".")[-1]:
                o[key] = value
        return o

    @locked
    def sync(self, *args, **kwargs):
        """ sync to disk using provided/created path. Optionally a path can be provided. """
        from .space import cfg, kernel
        from .static import headertxt
        path = None
        if self._fixed:
            path = self._Fixed
        if not path:
           try:
                path = args[0]
           except IndexError:
                path = None
        if not path:
            path = get_path(self)
        if not path:
            path = self._path
            stime = kwargs.get("stime", None)
            if stime:
                path = os.path.join(path, stime)
            else:
                path = os.path.join(path, rtime())
        if not path or not cfg.workdir in path:
            path = os.path.join(cfg.workdir, "typed", sname(self), rtime())
        path = os.path.abspath(os.path.normpath(path))
        logging.info("# sync %s" % os.sep.join(path.split(os.sep)[-3:]))
        if not cfg.workdir in path:
            raise EBORDER(path)
        self._container.path = path
        self._container.saved = time.ctime()
        d, fn = os.path.split(path)
        if not os.path.exists(d):
            cdir(d)
        todisk = self.prepare()
        rpath = path + "_tmp"
        try:
            datafile = open(rpath, 'w')
            fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            datafile = open(rpath, 'w')
            fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        datafile.write(headertxt % "%s characters" % len(todisk))
        datafile.write(todisk)
        datafile.write("\n")
        datafile.flush()
        os.rename(rpath, path)
        fcntl.flock(datafile, fcntl.LOCK_UN)
        datafile.close()
        return path

    def clear(self):
        """ clear the ready flag. """
        self._ready.clear()

    def isSet(self):
        """ check whether ready flag is set. """
        return self._ready.isSet()

    def ready(self):
        """ signal this object as "ready". """
        self._ready.set()

    def wait(self, timeout=None):
        """ wait for this object's ready flag. """
        self._ready.wait(timeout)
        result = []
        for thr in self._thrs:
            try:
                res = thr.join(timeout)
                result.append(res)
                self._thrs.remove(thr)
            except RuntimeError:
                pass
        return result

class Default(Object):

    """
        a Object with a "default" set. Standard default return is Object().

    """

    def __init__(self, *args, **kwargs):
        """ constructor that initializes a variable with Object() as a default. """
        super().__init__(*args, **kwargs)
        self.default = kwargs.get("default", "")

    def __getattr__(self, name):
        """ override Object.__getattr__.  """
        try:
            return super().__getattr__(name)
        except AttributeError as ex:
            self[name] = self.default
        return self[name]

class Config(Default):

    """
        a config object can read previous cfg from disk.

    """

    default = ""

    def __exec__(self):
        print(self.nice())

    def template(self, name):
        """ load a template into the config. """
        from botlib.template import template
        self.update(template.get(name, {}))
        return self

    def fromdisk(self, name):
        """ load the config from file. """
        from botlib.space import cfg
        self.template(name)
        self.cache(os.path.join(cfg.workdir, "config", name))
        if name == "xmpp":
            if cfg.room:
                self.room = cfg.room
            if cfg.server:
                self.server = cfg.server
        if name == "irc":
            if cfg.channel:
                self.channel = cfg.channel
            if cfg.nick:
                self.nick = cfg.nick
            if cfg.server:
                self.server = cfg.server
        if cfg.write:
            self.save()
        return self

def slice(obj, keys=[], skip=[], full=False):
    """ return a slice of an object. """
    o = Object()
    if not keys:
        keys = obj.keys()
    for key in keys:
        if key in skip:
            continue
        if not full and key.startswith("_"):
            continue
        val = obj.get(key, None)
        if val and "keys" in dir(val):
            o[key] = slice(val)
        else:
            o[key] = val
    return o

def dumped(o):
    """ add type string to an object attributes. """
    from .static import nodict_types
    if "items" not in dir(o):
        return o
    if type(o) == dict:
        o = Object(o)
    o._type = str(type(o))
    for k, v in o.items():
        if k == "_type":
            continue
        if type(v) in nodict_types:
            o[k] = v
        else:
            o[k] = dumped(v)
    return o
