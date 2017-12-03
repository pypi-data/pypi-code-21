# BOTLIB Framework to program bots
#
# botlib/cmnds.py
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

""" botlib basic commands. """

from .clock import Timed, Timers
from .compose import compose
from .object import Object, slice
from .template import template
from .utils import day, elapsed, now, to_date, to_day, to_time, parse_time
from .utils import sname

import botlib.space
import _thread
import logging
import mailbox
import time
import json
import sys
import os

psformat = "%-4s %-8s %-24s %-4s %6s %6s"

starttime = time.time()

def shutdown(event):
    """ close commands plugins. """
    pass

class Entry(Object):
    """ data entry class . """
    pass

class Log(Entry):
    """ a log entry to log what is happening on the day. """
    pass


class Rss(Entry):
    """ rss entry """
    pass

class Shop(Entry):
    """ shopping item for the wife to shop. """
    pass

class Todo(Entry):
    """ todo entry """
    pass

class Tomorrow(Entry):
    """ todo for tomorrow to be done. """
    pass

class Watch(Entry):
    """ files to watch. """
    pass

def license(event):
    """ display BOTLIB license. """
    from botlib import __license__
    event.reply(__license__)

license.perm = "USER"

def alias(event):
    """ key, value alias. """
    import botlib.space
    try:
        cmnd, value = event._parsed.rest.split(" ", 1)
    except ValueError:
        event.reply('alias <cmnd> <aliased>')
        return
    if value not in kernel._names:
        event.reply("only commands can be aliased.")
        return
    botlib.space.alias[cmnd] = value
    botlib.space.save()
    event.ok(cmnd)
    
alias.perm = "USER"

def announce(event):
    """ announce text on all channels in fleet. """
    kernel.announce(event._parsed.rest)
    event._result.append(event._parsed.rest)

announce.perm = "ANNOUNCE"

def attr(event):
    if not event._parsed.args:
         options = ",".join(os.listdir(_cfg.workdir))
         event.reply("attr <prefix>, use one of %s" % options)
         return
    prefix = event._parsed.args[0]
    try:
        keys = event._parsed.args[1:]
    except:
        keys = []
    obj = db.last(prefix)
    if obj:
        for key in keys:
            obj = getattr(obj, key, None)
        try:
            res = obj.keys()
        except AttributeError:
            res = []
            for o in obj:
                res.extend(o.keys())
            res = set(res)
        event.reply("\n".join(sorted([x for x in res if not x.startswith("_")])))
    else:
        event.reply("no %s prefix found." % event._parsed.args[0])

def begin(event):
    """ begin stopwatch. """
    t = to_time(now())
    event.reply("time is %s" % time.ctime(t))

begin.perm = "USER"

def cfg(event):
    """ edit config files. """
    from .space import cache
    args = event._parsed.args
    if not args:
        event.reply(_cfg)
        return
    name = args[0]
    if name not in template.keys():
        event.reply("%s config doesn't exist" % name)
        return
    p = os.path.abspath(os.path.join(_cfg.workdir, "config", name))
    if p in cache:
        obj = cache[p]
    else:
        obj = Config()
        obj.fromdisk(name)
    try:
        key = args[1]
    except IndexError:
        event.reply(obj)
        return
    if key not in obj:
        event.reply("EKEY %s" % key)
        return
    val = ""
    if len(args) > 3:
        val = args[2:]
    elif len(args) == 3:
        val = args[2]
    elif key in obj:
        event.reply("%s: %s" % (key, obj[key]))
        return
    else:
        event.reply("EKEY %s" % key)
    try:
        val = int(val)
    except:
        try:
            val = float(val)
        except:
            pass
    if type(val) == list:
        obj[key] = list(val)
    elif val in ["True", "true"]:
        obj[key] = True
    elif val in ["False", "false"]:
        obj[key] = False
    else:
        try:
            val = '"%s"' % val
            obj[key] = json.loads(val)
        except (SyntaxError, ValueError) as ex:
            event.reply("%s: %s" % (str(ex), val))
            return
    if key == "user" and "@" in obj[key]:
        obj["username"], obj["server"] = obj[key].split("@")
    obj.sync(os.path.join(_cfg.workdir, "config", name))
    event.ok(val)

cfg.perm = "CFG"

def edit(event):
    """ edit and save objects. """
    args = event._parsed.args
    if not args:
        event.reply(",".join(botlib.space.__all__))
        return
    name = args[0]
    if name not in botlib.space.__all__:
        event.reply("%s is not an object in botlib.space." % name)
        return
    obj = getattr(botlib.space, name)
    try:
        key = args[1]
    except IndexError:
        event.reply(obj)
        return
    if len(args) > 3:
        val = args[2:]
    elif len(args) == 3:
        val = args[2]
    else:
        event.reply("%s: %s" % (key, value))
        return
    set_space(name, key, val)
    event.ok(key, val)

edit.perm = "EDIT"

def cmnds(event):
    """ show list of commands. """
    res = sorted(set([cmnd for cmnd, mod in kernel._names.items() if event._parsed.rest in str(mod)]))
    event.reply(",".join(res) or "no modules loaded.")

cmnds.perm = "USER"

def deleted(event):
    """ show deleted records. """
    event.nodel = True
    nr = 0
    for obj in db.selected(event):
        if "deleted" in dir(obj) and obj.deleted:
            nr += 1
            event.display(obj, str(nr))

deleted.perm = "USER"

def delperm(event):
    """ delete permissions of an user. """
    try:
        nick, perm = event._parsed.args
    except:
        event.reply("delperm <origin> <perm>")
        return
    origin = fleet.get_origin(nick)
    if not origin:
        origin = nick
    result = users.delete(origin, perm)
    if not result:
        event.reply("can't find user %s" % origin)
        return
    event.ok(origin, perm)

delperm.perm = "OPER"

def end(event):
    """ stop stopwatch. """
    diff = time.time() - starttime
    if diff:
        event.reply("time elapsed is %s" % elapsed(diff))

end.perm = "USER"

def exit(event):
    """ stop the bot. """
    _thread.interrupt_main()

exit.perm = "EXIT"

def fetcher(event):
    """ fetch all rss feeds. """
    clients = runtime.get("RSS", [])
    if not clients:
        thr = kernel.init("botlib.rss")
        thr.join()
        clients = runtime.get("RSS", [])
    for client in clients:
        c = compose(client)
        thrs = c.fetcher()
        res = launcher.waiter(thrs)
        if res:
            event.reply("fetched %s" % ",".join(res))
        else:
            event.reply("fetched none")

fetcher._threaded = True
fetcher.perm = "RSS"

def fix(event):
    """ fix a object by loading and saving it. """
    fn = event._parsed.rest
    fn = os.path.abspath(fn)
    if not fn:
        event.reply("fix <path>")
        return
    if not os.path.isfile(fn):
        event.reply("%s is not a file" % fn)
        return
    o = Object()
    o.load(fn)
    p = o.save()
    event.reply("saved %s" % p)

fix.perm = "OPER"

def find(event):
    """ present a list of objects based on prompt input. """
    nr = 0
    seen = []
    for obj in db.selected(event):
        for key in event._parsed.uniqs.keys():
            val =  getattr(obj, key, None)
            if val and val in seen:
                continue
            else:
                seen.append(val)
        if "d" in event._parsed.enabled:
            event.reply(obj)
        else:
            event.display(obj, str(nr))
        nr += 1

find.perm = "USER"

def first(event):
    """ show the first record matching the given criteria. """
    obj = db.first(*event._parsed.args)
    if obj:
        event.reply(obj)

first.permn = "USER"

def last(event):
    """ show last objectect matching the criteria. """
    if not event._parsed.args:
        event.reply("last <prefix> <value>")
        return
    obj = db.last(*event._parsed.args)
    if obj:
        event.reply(obj)

last.perm = "USER"

def load(event):
    """ force a plugin reload. """
    if not event._parsed.rest:
        event.reply(",".join([x.split(".")[-1] for x in kernel.modules("botlib")]))
        return
    for modname in kernel.modules("botlib"):
        if event._parsed.rest not in modname:
            continue
        try:
            mod = kernel.reload(modname, True)
            event.reply("load %s" % modname)
        except (AttributeError, KeyError) as ex:
            event.reply("%s %s" % (modname, str(ex)))

load.perm = "LOAD"

def log(event):
    """ log some text. """
    if not event._parsed.rest:
        event.reply("log <item>")
        return
    o = Log()
    o.log = event._parsed.rest
    o.save()
    event.ok(1)

log.perm = "USER"

def loglevel(event):
    """ set loglevel. """
    from botlib.log import loglevel as _loglevel
    level = event._parsed.rest
    if not level:
        event.reply("loglevel is %s" % _cfg.loglevel)
        return
    oldlevel = _cfg.loglevel
    botlib.space.loglevel = level
    kernel.sync(os.path.join(_cfg.workdir, "runtime", "kernel"))
    try:
        _loglevel(level)
    except ValueError:
        try:
            _loglevel(oldlevel)
        except ValueError:
            pass
    event.reply("loglevel is %s" % level)

loglevel.perm = "LOGLEVEL"

def loud(event):
    """ disable silent mode of a bot. """
    for bot in fleet:
        if event.id() == bot.id():
            bot.cfg.silent = False
            bot.cfg.sync()
            event.reply("silent mode disabled.")

loud.perm = "LOUD"

def ls(event):
    """ show subdirs in working directory. """
    event.reply(" ".join(os.listdir(_cfg.workdir)))

ls.perm = "USER"

def man(event):
    """ show descriptions of the available commands. """
    res = sorted(set([cmnd for cmnd, mod in kernel._names.items() if event._parsed.rest in str(mod)]))
    for cmnd in res:
        description = kernel._descriptions.get(cmnd, "")
        if description:
            event.reply("%-20s %s" % (cmnd, description))

man.perm = "USER"

def nick(event):
    """ change bot nick on IRC. """
    bot = fleet.get_bot(event.id())
    if event._parsed.args:
        nick = event._parsed.args[0]
        bot.nick(nick)
        event.reply("nick changed to %s" % nick)
    else:
        event.reply("nick <name>")
        return

nick.perm = "OPER"

def pid(event):
    """ show pid of the BOTLIB bot. """
    event.reply("pid is %s" % str(os.getpid()))

pid.perm = "USER"

def permissions(event):
    """ show permissions granted to a user. """
    for name, funcs in kernel._handlers.items():
        if event._parsed.rest in name:
            event.reply("permissions are %s" % ",".join([str(x.perm) for x in funcs if "perm" in dir(x)]))

permissions.perm = "USER"

def ps(event):
    """ show running threads. """
    from .utils import name
    up = elapsed(int(time.time() - kernel._time.start))
    result = []
    for thr in sorted(launcher.running(), key=lambda x: name(x)):
        obj = Object(vars(thr))
        if "sleep" in obj:
            up = obj.sleep - int(time.time() - obj._time.latest)
        else:
            up = int(time.time() - obj._time.start)
        thrname = name(thr)[1:] + ")"
        result.append((up, thrname, obj))
    nr = 0
    for up, thrname, obj in sorted(result, key=lambda x: x[0]):
        nr += 1
        res = psformat % (nr, elapsed(up), thrname[:30], obj._state.printable(nokeys=True), obj._counter.printable(reverse=False), obj._error.printable(nokeys=True))
        event.reply(res.rstrip())

ps.perm = "PS"

def meet(event):
    """ create an user record. """
    try:
        origin = event._parsed.rest
    except:
        event.reply("meet <nick> [<perm1> <perm2>]")
        return
    orig = fleet.get_origin(origin)
    if not orig:
        orig = origin
    orig = orig.strip()
    if orig:
       u = users.meet(orig)
       if u:
           event.reply("user %s created" % origin)
       else:
           event.reply("%s is already introduced." % origin)

meet.perm = "MEET"

def perm(event):
    """ add/change permissions of an user. """
    try:
        nick, perms = event._parsed.args
    except:
        event.reply("perm <origin> <perm>")
        return
    origin = fleet.get_origin(nick)
    if not origin:
        origin = nick
    u = users.perm(origin, perms)
    if not u:
        event.reply("can't find a user matching %s" % origin)
        return
    event.ok(origin)

perm.perm = "OPER"

def perms(event):
    """ show permission of user. """
    u = users.fetch(event.origin)
    if u:
        event.reply("permissions are %s" % ",".join(u.perms))

perms.perm = "USER"

def real_reboot():
    """ actual reboot. """
    from .utils import reset
    kernel.shutdown(write=False)
    #kernel.wait()
    reset()
    os.execl(sys.argv[0], *(sys.argv + ["-r",]))

real_reboot.perm = "OPER"

def reboot(event):
    """ reboot the bot, allowing statefull reboot (keeping connections alive). """
    if not _cfg.reboot:
        event.reply("# reboot is not enabled.")
        return
    event.announce("rebooting")
    real_reboot()

reboot.perm = "OPER"

def reload(event):
    """ reload a plugin. """
    if not event._parsed.rest:
        event.reply(",".join([x.split(".")[-1] for x in kernel.modules("botlib")]))
        return
    for modname in kernel.modules("botlib"):
        if event._parsed.rest not in modname:
            continue
        try:
            mod = kernel.reload(modname, False)
            if mod:
                event.ok(modname)
            else:
                event.reply("no %s module foudn to reload." % modname)
        except (AttributeError, KeyError) as ex:
            event.reply("%s %s" % (modname, str(ex)))

reload.perm = "RELOAD"

def restore(event):
    """ set deleted=False in selected records. """
    nr = 0
    event.nodel = True
    for obj in db.selected(event):
        obj.deleted = False
        obj.sync()
        nr += 1
    event.ok(nr)

restore.perm = "RESTORE"

def rm(event):
    """ set deleted flag on objects. """
    nr = 0
    for obj in db.selected(event):
        obj.deleted = True
        obj.sync()
        nr += 1
    event.ok(nr)

rm.perm = "RM"

def rss(event):
    """ add a rss url. """
    if not event._parsed.rest:
        event.reply("rss <item>")
        return
    o = Rss()
    o.rss = event._parsed.rest
    o.service = "rss"
    o.save()
    event.ok(1)

rss.perm = "USER"

def silent(event):
    """ put a bot into silent mode. """
    for bot in fleet:
        if event.id() == bot.id():
            bot.cfg.silent = True
            bot.cfg.sync()
            event.reply("silent mode enabled.")
            return
    event.reply("no %s bot found in the fleet." % event.id())

silent.perm = "SILENT"

def shop(event):
    """ add a shopitem to the shopping list. """
    if not event._parsed.rest:
        event.reply("shop <item>")
        return
    o = Shop()
    o.shop = event._parsed.rest
    o.save()
    event.ok(1)

shop.perm = "USER"

def show(event):
    """ show dumps of basic objects. """
    if not event._parsed.rest:
        event.reply("choose one of alias, db, cfg, exceptions, fleet, kernel, launcher, partyline, runtime, seen or users")
        return
    try:
        item, value = event._parsed.rest.split(" ", 1)
    except:
        item = event._parsed.rest
        value = None
    if item == "bot":
        bots = fleet.get_bot(event.id())
        for bot in bots:
            event.reply(bot)
        return
    if item == "fleet":
        for bot in fleet:
            if value:
                val = getattr(bot, value, None)
                event.reply("%s=%s" % (value, val))
            else:
                event.reply(bot)
        return
    obj = getattr(botlib.space, item, None)
    if value:
        val = getattr(obj, value, None)
        event.reply("%s: %s" % (value, val))
    else:
        event.reply(obj)

show.perm = "SHOW"

def save(event):
    """ make a kernel dump. """
    from .space import save as _save
    _save()
    event.reply("saved")

save.perm = "SAVE"

def start(event):
    """ start a plugin. """
    modnames = kernel.modules("botlib")
    if not event._parsed.rest:
        res = set([x.split(".")[-1] for x in modnames])
        event.reply("choose one of %s" % ",".join(sorted(res)))
        return
    modname = event._parsed.args[0]
    name = "botlib.%s" % modname
    if name not in modnames:
        event.reply("no %s module found." % name)
        return
    mod = kernel.load(name, force=True)
    if "init" in dir(mod):
        mod.init(event)
    event.ok(name)

start.perm = "START"
start._threaded = True

def stop(event):
    """ stop a plugin. """
    if not event._parsed.rest:
        event.reply("stop what ?")
        return
    name = "botlib.%s" % event._parsed.args[0]
    try:
        mod = kernel._table[name]
    except KeyError:
        event.reply("no %s module available." % name)
        return
    if "shutdown" in dir(mod):
        mod.shutdown(event)
    event.ok(event.txt)

stop._threaded = True
stop.perm = "STOP"

def synchronize(event):
    """ synchronize rss feeds (fetch but don't show). """
    clients = runtime.get("RSS", [])
    for client in clients:
        c = compose(client)
        seen = c.synchronize()
        event.reply("%s urls updated" % len(seen.urls))

synchronize.perm = "SYNCHRONIZE"

def test(event):
    """ echo origin. """
    from .utils import stripped
    event.reply("hello %s" % stripped(event.origin))

test.perm = "USER"

def timer(event):
    """ timer command to schedule a text to be printed on a given time. stopwatch to measure elapsed time. """
    if not event._parsed.rest:
        event.reply("timer <string with time> <txt>")
        return
    seconds = 0
    line = ""
    try:
        target = parse_time(event.txt)
    except ValueError:
        event.reply("can't detect time")
        return
    if not target or time.time() > target:
        event.reply("already passed given time.")
        return
    t = Timed()
    t.services = "clock"
    t.prefix = "timer"
    t.txt = event._parsed.rest
    t.time = target
    t.done = False
    t.save()
    if "timers" not in runtime:
        runtime["timers"] = Timers()
    runtime["timers"].timers[t.time] = t
    event.ok(time.ctime(target))

timer.perm = "USER"

def today(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day())
    event._parsed.end = time.time()
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

today.perm = "USER"

def todo(event):
    """ log a todo item. """
    if not event._parsed.rest:
        event.reply("todo <item>")
        return
    o = Todo()
    o.todo = event._parsed.rest
    o.save()
    event.ok(1)

todo.perm = "USER"

def tomorrow(event):
    """ show todo items for tomorrow. """
    if not event._parsed.rest:
        event.reply("tomorrow <item>")
        return
    o = Tomorrow()
    o.tomorrow = event.txt.replace("tomorrow", "").strip()
    o.save()
    event.ok(1)

tomorrow.perm = "USER"

def u(event):
    """ show user selected by userhost. """
    if not event._parsed.rest:
        event.reply("u <origin>")
        return
    nick = event._parsed.args[0]
    origin = fleet.get_origin(nick)
    u = users.fetch(origin)
    if u:
        event.reply(u.pure())
    else:
        event.reply("no user %s found." % nick)

u.perm = "USER"

def w(event):
    """ show user data. """
    u = users.fetch(event.origin)
    if u:
        event.reply(u)
    else:
        event.reply("no matching user found.")

w.perm = "USER"

def uptime(event):
    """ show uptime. """
    event.reply("uptime is %s" % elapsed(time.time() - botlib._starttime))

uptime.perm = "USER"

def version(event):
    """ show version. """
    from botlib import __version__, __txt__
    event.reply("BOTLIB #%s - %s" % (__version__, __txt__))

version.perm = "USER"

def watch(event):
    """ add a file to watch (monitor and relay to channel). """
    if not event._parsed.rest:
        event.reply("watch <item>")
        return
    o = Watch()
    o.watch = event._parsed.rest
    o.save()
    event.ok(1)

watch.perm = "WATCH"

def week(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day()) - 7 * 24 * 60 * 60
    event._parsed.end = time.time()
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

week.perm = "USER"

def whoami(event):
    """ show origin. """
    event.reply("you have origin %s" % event.origin)

whoami.perm = "USER"

def yesterday(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day()) - 24 * 60 * 60
    event._parsed.end = to_day(day())
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

yesterday.perm = "USER"

