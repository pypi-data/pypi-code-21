# BOTLIB Framework to program bots
#
# botlib/irc.py
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

""" IRC bot class. """

from .bot import Bot
from .compose import compose
from .decorator import locked
from .event import Event
from .fleet import Fleet
from .error import EDISCONNECT
from .object import Object
from .space import cfg, fleet, kernel, launcher
from .utils import name, spath, split_txt

from botlib import __version__

import logging
import _thread
import random
import socket
import queue
import time
import ssl
import os

def init(*args, **kwargs):
    """ initialise a IRC bot. """
    bot = IRC()
    bot.start()
    return bot

def shutdown(event):
    """ stop all IRC bots. """
    for bot in fleet.get_type("irc"):
        bot.stop()

class IRC(Bot):

    """ Bot to connect to IRC networks. """

    cc = "!"
    default = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = []
        self._handlers.register("263", self.h263)
        self._handlers.register("315", self.h315)
        self._handlers.register("352", self.h352)
        self._handlers.register("353", self.h353)
        self._handlers.register("366", self.h366)
        self._handlers.register("376", self.connected)
        self._handlers.register("433", self.h433)
        self._handlers.register("ERROR", self.errored)
        self._handlers.register("MODE", self.moded)
        self._handlers.register("PING", self.pinged)
        self._handlers.register("PONG", self.ponged)
        self._handlers.register("QUIT", self.quited)
        self._handlers.register("INVITE", self.invited)
        self._handlers.register("PRIVMSG", self.privmsged)
        self._handlers.register("NOTICE", self.noticed)
        self._handlers.register("JOIN", self.joined)
        self._last = time.time()
        self._lastline = ""
        self._lock = _thread.allocate_lock()
        self._oldsock = None
        self._outqueue = queue.Queue()
        self._sock = None
        self._state.status = "run"
        self._userhosts = Object()
        self._threaded = False
        if self.cfg.channel and self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
            
    def _bind(self):
        """ find the internet adress of the IRC server (uses DNS). """
        server = self.cfg.server
        try:
            self._oldsock.bind((server, 0))
        except socket.error:
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET6, self.cfg.server)
                except socket.error:
                    pass
                else:
                    server = self.cfg.server
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET, self.cfg.server)
                except socket.error:
                    pass
                else:
                    server = self.cfg.server
            if not server:
                ips = []
                try:
                    for item in socket.getaddrinfo(self.cfg.server, None):
                        if item[0] in [socket.AF_INET, socket.AF_INET6] and item[1] == socket.SOCK_STREAM:
                            ip = item[4][0]
                            if ip not in ips:
                                ips.append(ip)
                except socket.error:
                    pass
                else: server = random.choice(ips)
        return server

    def _connect(self):
        """ create IRC socket, configure it and connect. """
        self._connected.clear()
        if self.cfg.ipv6:
            self._oldsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self._oldsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfg.server = self._bind()
        self._error.status = ""
        self._cfg()
        
    def _cfg(self):
        """ configure the IRC socket. """
        self.blocking = True
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(60.0)
        if not cfg.resume:
            logging.warn("# connect %s:%s" % (self.cfg.server, self.cfg.port or 6667))
            self._oldsock.connect((self.cfg.server, int(str(self.cfg.port or 6667))))
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(700.0)
        self.fsock = self._oldsock.makefile("r")
        if self.cfg.ssl:
            self._sock = ssl.wrap_socket(self._oldsock)
        else:
            self._sock = self._oldsock
        self._sock.setblocking(self.blocking)
        self._resume.fd = self._sock.fileno()
        if cfg.reboot:
            os.set_inheritable(self._resume.fd, os.O_RDWR)
        self.register_fd(self._sock)

    def _output(self):
        """ output loop reading from _outqueue. """
        self._connected.wait()
        while not self._stopped:
            args = self._outqueue.get()
            if not args or self._stopped:
                break
            self.out(*args)
            
    def _some(self):
        """ read from socket, add to buffer and return last line. """
        try:
            if self.cfg.ssl:
                inbytes = self._sock.read()
            else:
                inbytes = self._sock.recv(512)
        except ConnectionResetError:
            raise EDISCONNECT(self.cfg.server)
        txt = str(inbytes, self.cfg.encoding)
        if txt == "":
            raise EDISCONNECT(self.cfg.server)
        self._lastline += txt
        splitted = self._lastline.split("\r\n")
        for s in splitted[:-1]:
            self._buffer.append(s)
            if not s.startswith("PING") and not s.startswith("PONG"):
                logging.warn("< %s" % s.strip())
        self._lastline = splitted[-1]

    def announce(self, txt):
        """ announce txt to all joined channels. """
        for channel in self.channels:
            self._outqueue.put_nowait((channel, txt))

    def close(self):
        """ close the irc sockets, """
        if self.ssl:
            self.oldsock.shutdown(1)
            self.oldsock.close()
        else:
            self._sock.shutdown(1)
            self._sock.close()
        self.fsock.close()

    def connect(self, event=None):
        """ connect to server. """
        if cfg.resume:
            self._stopped = False
            self._counter.resume += 1
            self.resume()
            return
        self._stopped = False
        self._counter.connect += 1
        try:
            self._connect()
            time.sleep(2)
            self.logon()
        except Exception as ex:
            e = Event()
            e.command = e.cmnd = "ERROR"
            e.txt = str(ex).lower()
            self.put(e)
  
    def dispatch(self, event):
        """ function called to dispatch event to it's handler. """
        for handler in self._handlers.get(event.command, []):
            handler(event)
            self._state.status = name(handler)

    def direct(self, txt):
        if not txt.startswith("PING") and not txt.startswith("PONG"):
            logging.warn("> %s" % txt)
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt = bytes(txt, "utf-8")
        self._last = time.time()
        try:
            self._sock.send(txt)
            return
        except (BrokenPipeError, ConnectionResetError):
            pass
        except AttributeError:
            try:
                self._sock.write(txt)
                return
            except (BrokenPipeError, ConnectionResetError):
                return

    def event(self):
        """ return an event from the buffer (if available). """
        if not self._buffer:
            self._some()
        line = self._buffer.pop(0)
        e = self.parsing(line.rstrip())
        e.btype = self.type
        return e

    def join(self, channel, password=""):
        """ join a channel. """
        if password:
            self.direct('JOIN %s %s' % (channel, password))
        else:
            self.direct('JOIN %s' % channel)
        if channel not in self.channels:
            self.channels.append(channel)

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def logon(self, *args):
        """ logon to the IRC network. """
        self.direct("NICK %s" % self.cfg.nick)
        self.direct("USER %s %s %s :%s" % (self.cfg.username,
                                                  self.cfg.server,
                                                  self.cfg.server,
                                                  self.cfg.realname))

    @locked
    def out(self, channel, line):
        """ output method, split into 375 char lines, sleep 3 seconds. """
        line = str(line)
        for txt in line.split("\n"):
            if time.time() - self._last < 3.0:
                time.sleep(3.0)
            self.privmsg(channel, txt)

    def parsing(self, txt):
        """ parse txt line into an Event. """
        rawstr = str(txt)
        obj = Event()
        obj.txt = ""
        obj.cc = self.cc
        obj.arguments = []
        arguments = rawstr.split()
        obj.origin = arguments[0]
        if obj.origin.startswith(":"):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                    obj.txt = " ".join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.cfg.server
        try:
            obj.nick, obj.origin = obj.origin.split("!")
        except:
            pass
        if obj.arguments:
            obj.target = obj.arguments[-1]
        else:
            obj.target = "" 
        if obj.target.startswith("#"):
            obj.channel = obj.target
        else:
            obj.channel = obj.nick
        if not obj.txt and len(arguments) == 1:
            obj.txt = arguments[1]
        if not obj.txt:
            obj.txt = rawstr.split(":")[-1]
        obj.id = self.id()
        obj.cb = obj.command
        return obj

    def part(self, channel):
        """ leave a channel. """
        self.raw('PART %s' % channel)
        if channel in self.channels:
            self.channels.remove(channel)

    def raw(self, txt):
        """ send txt over the socket to the server. """
        if self._error.status:
            return
        self.direct(txt)

    def resume(self):
        """ resume the bot after reboot, creating stateless reboot. """
        from .space import kernel
        self._connected.clear()
        fn = os.path.join(cfg.workdir, "runtime", "fleet")
        logging.warn("# resume %s" % spath(fn))
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
                self.channels = bot["channels"]
                logging.warn("# resume %s %s" % (fd, ",".join([str(x) for x in self.channels])))
                if self.cfg.ipv6:
                    self._oldsock = socket.fromfd(fd, socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    self._oldsock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
                self._cfg()
                self.announce("done")
                break
        self.ready()

    def say(self, channel, txt, type=""):
        """ say txt on a channel. """
        self._outqueue.put_nowait((channel, txt))

    def start(self, *args, **kwargs):
        """ start the IRC bot. """
        self.reconnect()
        launcher.launch(self._output)
        super().start(*args, **kwargs)

    def stop(self):
        """ stop the IRC bot. """
        super().stop()
        self.quit("http://bitbucket.org/bthate/botlib")
        self._stopped = True
        self._outqueue.put(None)
        self.ready()

    def noticed(self, event):
        """ called when the bot is being noticed. """
        pass

    ## callbacks

    def connected(self, event):
        """ called when the bot is connected. """
        if "servermodes" in self.cfg:
            self.direct("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
        self._connected.ready()
        self.joinall()
        self._state.status = "run"

    def errored(self, event):
        """ error handler. """
        logging.error("# error %s" % event)
        self._error.status = event.txt.lower()
        if "closed" in event.txt or "refused" in event.txt or "disconnect" in event.txt:
            self.reconnect()

    def invited(self, event):
        """ called when the bot is invited to a channel. """
        self.join(event.channel)

    def joined(self, event):
        """ called when someone joined a channel. """
        channel = event.txt.split()[0]
        logging.warn("# joined %s" % channel)
        if self.cfg.logname in event.origin:
            self.ready()


    def moded(self, event):
        """ MODE callback. """
        if self.cfg.realname in event.origin:
            self.cfg.logname = event.origin

    def pinged(self, event):
        """ ping callback. """
        self.pongcheck = True
        self.pong(event.txt)

    def ponged(self, event):
        """ pong callback. """
        self.pongcheck = False

    def quited(self, event):
        """ called when someone quits IRC. """
        logging.error("# quit %s" % event.origin)
        if self.cfg.server in event.origin:
            self.stop()

    def privmsged(self, event):
        """ PRIVMSG callback, forwards the event to the kernel for handling. """
        if event.txt.startswith("\001VERSION"):
            self.ctcpreply(event.nick, "VERSION BOTLIB #%s - http://bitbucket.org/bthate/botlib" % __version__)
            return
        self._userhosts[event.nick] = event.origin
        kernel.put(event)

    def ctcped(self, event):
        """ called when the bot is CTCP'ed. """
        pass

    def h001(self, event):
        """ 001 handler. """
        pass

    def h002(self, event):
        """ 002 handler. """
        pass

    def h003(self, event):
        """ 003 handler. """
        pass

    def h004(self, event):
        """ 004 handler. """
        pass

    def h005(self, event):
        """ 005 handler. """
        pass

    def h263(self, event):
        """ 263 handlers. """
        logging.error("# h263 %s" % event)
        self.stop()

    def h315(self, event):
        """ 315 handler. """
        pass

    def h352(self, event):
        """ 352 handler. """
        args = event.arguments
        self._userhosts[args[5]] = args[2] + "@" + args[3]

    def h353(self, event):
        """ 353 handler. """
        pass

    def h366(self, event):
        """ 366 handler. """
        pass

    def h433(self, event):
        """ 433 handler. """
        self.nick(event.target + "_")

    def h513(self, event):
        """ 513 PING response handler. """
        self.raw("PONG %s" % event.arguments[-1])

    def nick(self, nick):
        """ change nick of the bot. """
        self.direct('NICK %s' % nick[:16])
        self.cfg.nick = nick

    ## RAW output

    def who(self, channel):
        """ send a WHO query. """
        self.direct('WHO %s' % channel)

    def names(self, channel):
        """ send a NAMES query. """
        self.raw('NAMES %s' % channel)

    def whois(self, nick):
        """ send a WHOIS query. """
        self.raw('WHOIS %s' % nick)

    def privmsg(self, channel, txt):
        """ send a PRIVMSG. """
        self.raw('PRIVMSG %s :%s' % (channel, txt))

    def voice(self, channel, nick):
        """ send a MODE +v. """
        self.raw('MODE %s +v %s' % (channel, nick))

    def doop(self, channel, nick):
        """ send a MODE +o. """
        self.raw('MODE %s +o %s' % (channel, nick))

    def delop(self, channel, nick):
        """ send a MODE -o. """
        self.raw('MODE %s -o %s' % (channel, nick))

    def quit(self, reason='http://bitbucket.com/bthate/botlib'):
        """ send a QUIT message with a reason for quitting. """
        self.raw('QUIT :%s' % reason)

    def notice(self, channel, txt):
        """ send NOTICE to channel/nick. """
        self.raw('NOTICE %s :%s' % (channel, txt))

    def ctcp(self, nick, txt):
        """ send CTCP to nick. """
        self.raw("PRIVMSG %s :\001%s\001" % (nick, txt))

    def ctcpreply(self, channel, txt):
        """ send a NOTICE message in reply to a CTCP message. """
        self.raw("NOTICE %s :\001%s\001" % (channel, txt))

    def action(self, channel, txt):
        """ send a /me ACTION. """
        self.raw("PRIVMSG %s :\001ACTION %s\001" % (channel, txt))

    def getchannelmode(self, channel):
        """ query channel modes. """
        self.raw('MODE %s' % channel)

    def settopic(self, channel, txt):
        """ set topic on a channel. """
        self.raw('TOPIC %s :%s' % (channel, txt))

    def ping(self, txt):
        """ send PING. """
        self.direct('PING :%s' % txt)

    def pong(self, txt):
        """ send PONG. """
        self.direct('PONG :%s' % txt)
