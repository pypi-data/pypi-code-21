# BOTLIB Framework to program bots
#
# botlib/test.py
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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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

""" plugin containing test commands and classes. """

from .event import Event
from .utils import get_name
from .trace import get_exception
from .space import cfg, fleet, kernel
from .template import varnames

import logging
import random
import types
import time

classes = ["Bot", "IRC", "XMPP", "CLI", "Event", "Handler", "Task", "Object", "Default", "Config", "Launcher"]

exclude = ["exit", "loglevel", "timer", "funcs", "reboot", "real_reboot", "fetcher", "synchronize", "init", "shutdown", "wrongxml", "tests"]
outtxt = u"Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"

waiting = []


def test():
    """ test function. """
    print("yooo!")

def randomarg():
    """ create a random typed argument to use in tests. """
    t = random.choice(classes)
    return types.new_class(t)()

def e(event):
    """ show a dump of an event after parsing. """
    event.reply(event.nice())

def flood(event):
    """ create a flood of characters. """
    txt = "b" * 5000
    event.reply(txt)

flood.perm = "FLOOD"

def forced(event):
    """ attempt a forced reconnect. """
    for bot in fleet:
        try:
            bot._sock.shutdown(2)
        except (OSError, AttributeError):
            pass

forced.perm = "FORCED"

def hammer(event):
    """ repeat commands. """
    try:
        nr, cmnd = event._parsed.rest.split(" ", 1)
        nr = int(nr)
    except ValueError:
        event.reply("hammer <nr> <cmnd>")
        return
    except:
        logging.error(get_exception())
        event.reply("hammer <nr> <cmnd>")
        return
    events = []
    for x in range(nr):
        e = Event(event)
        event.txt = cmnd
        kernel.put(event)
        events.append(event)
    for e in events:
        e.wait()

hammer.perm = "OPER"
hammer._threaded = True

if cfg.test:
    def exception(event):
        """ raise a test exception. """
        raise Exception('test exception')

    exception.perm = "exception"

def wrongxml(event):
    """ send some wrong xml over the wire. """
    event.reply('sending bork xml')
    for bot in fleet:
        bot.raw('<message asdfadf/>')

wrongxml.perm = "WRONGXML"

def unicode(event):
    """ output some unicode test. """
    event.reply(outtxt)

def deadline(event):
    """ sleep for 10 seconds. """
    try:
        nrseconds = int(event._parsed.rest)
    except:
        nrseconds = 10
    event.direct('starting %s sec sleep' % nrseconds)
    time.sleep(nrseconds)

deadline._threaded = True
deadline.perm = "DEADLINE"

def html(event):
    """ send some html over the wire. """
    event.reply('<span style="font-family: fixed; font-size: 10pt"><b>YOOOO BROEDERS</b></span>')


def tests(event):
    """ run all commands as events run through the kernel's handler. """
    from .space import events
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    try:
        nr = int(event._parsed.rest)
    except ValueError:
        nr = 10
    for x in range(nr):
        keys = list(kernel.list("botlib"))
        random.shuffle(keys)
        for cmnd in keys:
            if cmnd in exclude:
                continue
            if cmnd == "find":
                name = "email From=pvp"
            else:
                name = get_name(cmnd)
            e = Event()
            e.origin = "test@shell"
            e.txt = "%s %s" % (cmnd, name)
            kernel.put(e)
            events.append(e)
    event.direct("# wait %s" % len(events))
    for e in events:
        print(e)
        e.wait()
    event.reply("done")

tests._threaded = True
tests.perm = "TESTS"

def dofunc(func):
    """ run a function with tests arguments found by introspecting the call stack. """
    e = Event()
    if func and type(func) in [types.FunctionType, types.MethodType]:
        arglist = []
        nrvar = func.__code__.co_argcount
        for name in func.__code__.co_varnames:
            n = varnames.get(name, None)
            if n:
                arglist.append(n)
            else:
                arglist.append(e)
            logging.info("! funcs %s %s" % (func, ",".join([str(x) for x in arglist])))
            try:
                func(*arglist[:nrvar])
            except:
                logging.error(get_exception())

def funcs(event):
    """ do an introspection on all functions found in the bot and run them with random arguments. """
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    if not cfg.uber:
        event.reply("the uber option is not set.")
        return
    for name in sorted(kernel.modules("botlib")):
        mod = kernel.load(name)
        keys = dir(mod)
        random.shuffle(keys)
        for key in keys:
            if "_" in key:
                continue
            if key in exclude:
                continue
            obj = getattr(mod, key, None)
            dofunc(obj)
            for nkey in dir(obj):
                o = getattr(obj, nkey, None)
                if o:
                    dofunc(o)

funcs._threaded = True
funcs.perm = "FUNCS"
