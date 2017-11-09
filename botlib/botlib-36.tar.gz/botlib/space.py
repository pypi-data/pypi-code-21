# BOTLIB Framework to program bots
#
# botlib/space.py
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

""" central module to store objects in. """

__all__ = ["db", "cfg", "fleet", "kernel", "launcher", "pool", "profiler", "runner", "runtime", "users", "Config", "Default", "Event", "Object", "Timer", "locked", "get_exception", "set_space", "sname", "name"]

from .clock import Timer
from .db import Db
from .decorator import locked
from .defines import defaults
from .event import Event
from .fleet import Fleet
from .handler import Handler
from .kernel import Kernel
from .launcher import Launcher
from .object import Config, Default, Object
from .register import Register
from .runner import Runner
from .template import template
from .trace import get_exception
from .users import Users
from .utils import sname, name
from .worker import Pool

import os.path

alias = Object()
db = Db()
cache = Object()
cfg = Config(template.get("kernel"))
events = []
exceptions = []
fleet = Fleet()
kernel = Kernel()
launcher = Launcher()
profiler = Default(default=0)
pool = Pool()
profiler = Default(default=0)
reserved = Pool()
runner = Pool()
runtime = Register()
seen = Object(urls=[])
users = Users()

def set_space(name, key, value):
    """ set a space variable to the right value. """
    if name == "alias":
        alias[key] = value
        alias.save()
    elif name == "db":
        db[key] = value
        db.save()
    elif name == "cfg":
        cfg[key] = value
        cfg.save()
    elif name == "fleet":
        for bot in fleet:
            bot.cfg[key] = value
            bot.cfg.save()
    elif name == "kernel":
        kernel[key] = value
        kernel.save()
    elif name == "launcher":
        launcher[key] = value
        launcher.save()
    elif name == "runtime":
        runtime[key] = value
        runtime.save()
    elif name == "seen":
        seen[key] = value
        seen.save()
    elif name == "users":
        users[key] = value
        users.save()

def load():
    """ load basic objects (alias, seen and users). """
    alias.load(os.path.join(cfg.workdir, "runtime", "alias"))
    seen.load(os.path.join(cfg.workdir, "runtime", "seen"))
    users.load(os.path.join(cfg.workdir, "runtime", "users"))

def save():
    """ sace space objects to disks. """
    alias.sync(os.path.join(cfg.workdir, "runtime", "alias"))
    cfg.sync(os.path.join(cfg.workdir, "runtime", "cfg"))
    fleet.sync(os.path.join(cfg.workdir, "runtime", "fleet"))
    #kernel.sync(os.path.join(cfg.workdir, "runtime", "kernel"))
    seen.sync(os.path.join(cfg.workdir, "runtime", "seen"))

def clean(event):
    """ reset space. """
    pool.cleanup()
    reserved.cleanup()
