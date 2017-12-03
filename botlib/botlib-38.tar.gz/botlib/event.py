# BOTLIB Framework to program bots
#
# botlib/event.py
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

""" event handling classes. """

from .decorator import space
from .object import Default, Object, slice
from .register import Register
from .trace import get_exception
from .utils import days, make_opts, name, parse_time, sname

import logging
import optparse
import random

class Parsed(Default):

    """ parsed contains all the arguments that are _parsed from an event. """

    default = ""

    def __getattr__(self, name):
        if name == "args":
            self.args = []
        if name == "cmnd":
            self.cmnd = ""
        if name == "counter":
            self.counter = 0
        if name == "delta":
            self.delta = 0
        if name == "disabled":
            self.disabled = []
        if name == "enabled":
            self.enabled = []
        if name == "fields":
            self.fields = []
        if name == "index":
            self.index = None
        if name == "ignore":
            self.ignore = Register()
        if name == "notwant":
            self.notwant = Register()
        if name == "rest":
            self.rest = ""
        if name == "switch":
            self.switch = Register()
        if name == "uniqs":
            self.uniqs = Register()
        if name == "want":
            self.want = Register()
        if name == "words":
            self.words = []
        return super().__getattr__(name)

    def clear(self):
        self._nrparsed = 0
        self.args = []
        self.cmnd = ""
        self.counter = 0
        self.disabled = []
        self.enabled = []
        self.fields = []
        self.index = None
        self.ignore = Register()
        self.notwant = Register()
        self.rest = ""
        self.switch = Register()
        self.want = Register()
        self.words = []
        self.uniqs = Register()

    def parse(self, txt):
        """ parse txt to determine cmnd, args, rest and other values. adds a _parsed object to the event. """
        txt = str(txt)
        splitted = txt.split()
        quoted = False
        key2 = ""
        counter = -1
        for word in splitted:
            counter += 1
            if counter == 0:
                if self.command:
                    self.cmnd = self.command
                    continue
                if self.cc and self.cc != word[0]:
                    continue
                if self.cc:
                    word = word[1:]
                if word:
                    self.cmnd = word.lower().strip()
                continue
            try:
                key, value = word.split("=", 1)
            except (IndexError, ValueError):
                key = ""
                value = word
            if "http" in key:
                key = ""
                value = word
            if value.startswith('"'):
                if value.endswith('"'):
                    value = value[:-1]
                    self.words.append(value)
                else:
                    key2 = key
                    value = value[1:]
                    self.words.append(value)
                    quoted = True
                    continue
            if quoted:
                if '"' in value:
                    value, *restant = value.split('"')
                    key = key2
                    self.words.append(value)
                    value = " ".join(self.words)
                    value += "".join(restant)
                    self.words = []
                    quoted = False
                else:
                    self.words.append(value)
                    continue
            if quoted:
                self.words.append(value)
                continue
            if "http" in value:
                self.args.append(value)
                self.rest += value + " "
                continue
            if key == "index":
                self.index = int(value)
                continue
            if key == "start":
                if self.start:
                    continue
                self.start = parse_time(value)
                continue
            if key == "end":
                if self.stop:
                    continue
                self.end = parse_time(value)
                continue
            if key and value:
                post = value[0]
                last = value[-1]
                pre = key[0]
                op = key[-1]
                if key.startswith("!"):
                    key = key[1:]
                    self.switch.register(key, value)
                    continue
                if post == "-":
                    value = value[1:]
                    self.ignore.register(key, value)
                    continue
                if op == "-":
                    key = key[:-1]
                    self.notwant.register(key, value)
                    continue
                if pre == "^":
                    key = key[1:]
                    self.uniqs.register(key, value)
                if last == "-":
                    value = value[:-1]
                self.want.register(key, value)
                if last == "-":
                    continue
                if counter > 1:
                    self.fields.append(key)
                self.args.append(key)
                self.rest += key + " "
            elif value:
                post = value[0]
                last = value[-1]
                if post == "^":
                    value = value[1:]
                    self.uniqs.register(value, "")
                if value.startswith("+") or value.startswith("-"):
                    v = value[1:]
                    try:
                        val = int(value)
                        self.delta = 0 + (val * 60*60)
                        if val >= -10 and val <= 10:
                            self.karma = val
                    except ValueError:
                        pass
                    if post == "-":
                        if v not in self.enabled:
                            self.enabled.append(v)
                            continue
                    elif post == "+":
                        if v not in self.disabled:
                            self.disabled.append(v)
                            continue
                if counter > 1:
                    self.fields.append(value)
                self.args.append(value)
                self.rest += str(value) + " "
        self.rest = self.rest.strip()
        return self

class Event(Default):

    """ Events are constructed by bots based on the data they receive. This class provides all functionality to handle this data (parse, dispatch, show). """

    default = ""

    def __getattr__(self, name):
        if name == "origin":
            self["origin"] = self.id()
        if name == "cb":
            self["cb"] = self._type
        if name == "channel":
            self["channel"] = self.origin
        if name == "_denied":
            self._denied = ""
        if name == "_parsed":
            self._parsed = Parsed(slice(self, ["cc", "txt"]))
        if name == "_result":
            self._result = []
        if name == "_running":
            self._running = ""
        if name == "_threaded":
            self._threaded = False
        val = super().__getattr__(name)
        return val

    def add(self, txt):
        """ say something on a channel, using the bot available in the fleet. """
        self._result.append(txt)

    def announce(self, txt):
        """ announce on all fleet bot. """
        from .space import kernel
        kernel.announce(txt)

    def direct(self, txt):
        """ output txt directly. """
        from .space import fleet
        fleet.say_id(self.id(), self.channel, txt, self.type)

    def dispatch(self):
        """ dispatch the object to the functions registered in the _funcs member. """
        for func in self._funcs:
            self._running = func
            func(self)
 
    def display(self, obj=None, txt="", skip=False):
        """ display the content of an object.  """
        from .space import defaults
        keys = []
        res = ""
        if not obj:
            obj = self
        if "a" in self._parsed.enabled:
            keys = obj.keys()
        if not keys:
            keys = self._parsed.args
        for key in keys:
            val = getattr(obj, key, None)
            if val:
                res += str(val).strip() + " "
        if not res:
            keys = defaults.get(self._parsed.args[0], ["txt", ])
            for key in keys:
                val = getattr(obj, key, None)
                if val:
                    res += str(val).strip() + " "
        if txt and res:
            res = "%s %s" % (txt.strip(), res.strip())
        if obj and res:
            d = days(obj)
            if d:
                res += " - %s" % d
        res = res.strip()
        if res:
            self.reply(res)
        
    def id(self):
        """ return a bot type + server host as a event id. """
        return self.btype + "." + self.server

    def ok(self, *args):
        """ reply with 'ok'. """
        self.reply("ok %s" % "=".join([str(x) for x in args]))

    def parse(self, txt="", force=False):
        """ convenience method for the _parsed.parse() function. resets the already available _parsed. """
        from .space import kernel
        txt = txt or self.txt
        if not self._result:
            self._result = []
        self._parsed.clear()
        self._parsed.parse(txt)
        kernel.prep(self)
        
    def prompt(self):
        """ give a prompt on the corresponding cli bot. """
        from .space import fleet
        if self.btype != "cli":
            return
        bots = fleet.get_type("cli")
        for bot in bots:
            bot.prompt()

    def say_id(self, id, channel, txt):
        """ say something to id on fleet bot. """
        from .space import fleet
        fleet.say_id(id, channel, txt, self.type)

    def reply(self, txt):
        """ give a reply to the origin of this event. """
        if not self.batch:
             self.direct(txt)
        self.add(txt)

    def show(self):
        """ show the event on the server is originated on. """
        for txt in self._result:
            self.direct(txt)
