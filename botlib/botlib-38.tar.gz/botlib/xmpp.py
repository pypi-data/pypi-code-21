# BOTLIB Framework to program bots
#
# botlib/xmpp.py
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

""" XMPP bot class. """

from .bot import Bot
from .event import Event
from .object import Default, Object
from .utils import stripped
from .space import cfg, fleet, launcher
from .trace import get_exception

import os
import logging
import ssl
import time

def init(*args, **kwargs):
    """ initialize the xmpp bot. """
    bot = XMPP()
    bot.start()
    return bot

def shutdown(event):
    """ stop the xmpp bot. """
    for bot in fleet.get_type("xmpp"):
        bot.stop()
    launcher.kill("XMPP")

class XMPP(Bot):

    """" XMPP bot based on sleekxmpp. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threaded = False
        self._userhosts = Object()
        self.channels = []
        if self.cfg.room and self.cfg.room not in self.channels:
            self.channels.append(self.cfg.room)
        
    def _connect(self, user, pw):
        """ connect to the xmpp server. """
        self._makeclient(user, pw)
        self.client.reconnect_max_attempts = 3
        logging.warn("# connect %s" % user)
        if self.cfg.noresolver:
            self.client.configure_dns(None)
        if self.cfg.openfire:
            self.client.connect(use_ssl=True)
        else:
            self.client.connect(reattempt=True)
        self._connected.ready()
                
    def _makeclient(self, jid, password):
        """ create a sleekxmpp client to use. """
        try:
            import sleekxmpp.clientxmpp
            import sleekxmpp
        except ImportError:
            logging.warn("# sleekxmpp is not installed")
            return
        self.client = sleekxmpp.clientxmpp.ClientXMPP(str(jid), password)
        self.client._counter = Default(default=0)
        self.client._error = Object()
        self.client._state = Object()
        self.client._state.status = "running"
        self.client._time = Default(default=0)
        self.client._time.start = time.time()
        self.client.use_ipv6 = cfg.use_ipv6
        #self.client.ssl_version = ssl.PROTOCOL_TLS
        #self.client.ssl_version = ssl.PROTOCOL_SSLv3
        #self.client.ssl_version = ssl.PROTOCOL_SSLv23
        #self.client.ssl_version = ssl.PROTOCOL_TLSv1_2
        #self.client.ssl_version = ssl.PROTOCOL_TLSv1_1
        #self.client.ssl_version = ssl.PROTOCOL_SSLv23
        #self.client.do_handshake_on_connect = False
        #self.client.options |= ssl.OP_NO_SSLv2
        #self.client.options |= ssl.OP_NO_SSLv3
        if cfg.no_certs:
            self.client.ca_certs = ssl.CERT_NONE
            self.client.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
        self.client.register_plugin(u'xep_0030')
        self.client.register_plugin(u'xep_0045')
        self.client.register_plugin(u'xep_0199')
        self.client.register_plugin(u'xep_0203')
        self.client.add_event_handler("session_start", self.session_start)
        self.client.add_event_handler("message", self.messaged)
        self.client.add_event_handler("iq", self.iqed)
        self.client.add_event_handler("ssl_invalid_cert", self.invalid_cert)
        self.client.add_event_handler('disconnected', self.disconnected)
        self.client.add_event_handler('connected', self.connected)
        self.client.add_event_handler('presence_available', self.presenced)
        self.client.add_event_handler('presence_dnd', self.presenced)
        self.client.add_event_handler('presence_xa', self.presenced)
        self.client.add_event_handler('presence_chat', self.presenced)
        self.client.add_event_handler('presence_away', self.presenced)
        self.client.add_event_handler('presence_unavailable', self.presenced)
        self.client.add_event_handler('presence_subscribe', self.presenced)
        self.client.add_event_handler('presence_subscribed', self.presenced)
        self.client.add_event_handler('presence_unsubscribe', self.presenced)
        self.client.add_event_handler('presence_unsubscribed', self.presenced)
        self.client.add_event_handler('groupchat_presence', self.presenced)
        self.client.add_event_handler('groupchat_subject', self.presenced)
        self.client.add_event_handler('failed_auth', self.failedauth)
        self.client.exception = self.exception
        self.client.use_signals()

    def announce(self, txt):
        """ announce text on the joined channels. """
        for channel in self.channels:
            self.say(channel, txt)

    def connect(self, user, passwd=""):
        """ connect to the xmpp server. """
        if not passwd:
            fn = os.path.expanduser("~/.sleekpass")
            pww = ""
            f = open(fn, "r")
            pww = f.read()
            f.close()
            passwd = pww.strip()
        self.passwd = passwd
        self._connect(user, self.passwd)
        
    def connected(self, data):
        """ called when the bot is connected to the server. """
        self._connected.ready()
        if self.channels:
            self.joinall()
            logging.warn("# joined %s" % ",".join(self.channels))
        self.ready()
         
    def disconnected(self, data):
        """ disconnedted callback. """
        logging.warn("# disconnected %s" % data)

    def event(self):
        """" generate an event from the data in _queue. """
        e = self._queue.get()
        if e:
            e.btype = self.type
        return e

    def exception(self, data):
        """ exception callback. """
        logging.error("# error %s" % data)

    def failedauth(self, data):
        """ failedauth callback. """
        logging.info("# failed auth %s" % data)

    def failure(self, data):
        """ failure callback. """
        logging.info("# failure %s" % data)

    def invalid_cert(self, data):
        """ invalid certifcate callback. """
        logging.info("# invalid cert %s" % data)

    def iqed(self, data):
        """ iq callback. """
        logging.warn("! %s" % data)

    def join(self, room):
        self.client.plugin['xep_0045'].joinMUC(room,
                                    self.cfg.nick,
                                    wait=False)

    def messaged(self, data):
        """ function to handle messages from server. """
        from .space import kernel
        logging.warn("# message %s" % data)
        m = Event()
        m.update(data)
        if data["type"] == "error":
            logging.error("# error %s" % m.error)
            return
        if data["type"] == "groupchat":
            m.cc = "!"
            m.element = "groupchat"
            self._userhosts[m.nick] = str(m["from"])
        else:
            m.cc = ""
            m.element = "message"
        m["from"] = str(m["from"])
        if self.cfg.user in m["from"]:
            logging.warn("# ignore %s %s" % (m.type, m["from"]))
            return
        m.origin = m["from"]
        m.btype = "xmpp"
        m.server = self.cfg.server
        m.channel = m.origin
        m.to = m.origin
        m.txt = m["body"]
        m.cb = "Message"
        if '<delay xmlns="urn:xmpp:delay"' in str(data):
            logging.warn("! ignore %s" % m.origin)
            return
        kernel.put(m)

    def pinged(self, event):
        """ ping callback. """
        logging.info(event)

    def presenced(self, data):
        """ function to handle presences. """
        from .space import kernel
        logging.info("# presence %s" % data)
        o = Event()
        o.update(data)
        o.id = self.id()
        o.server = self.cfg.server
        o.cc = ""
        o.origin = str(data["from"])
        if "txt" not in o:
            o.txt = ""
        o.element = "presence"
        #user = stripped(o.origin)
        user = o.origin
        if o.type == 'subscribe':
            pres = Event({'to': o["from"], 'type': 'subscribed'})
            self.client.send_presence(pres)
            pres = Event({'to': o["from"], 'type': 'subscribe'})
            self.client.send_presence(dict(pres))
        elif o.type == "unavailable" and user != self.cfg.user and user in self.channels:
            self.channels.remove(user)
        elif self.cfg.user in user and user not in self.channels:
            self.channels.append(user)
        o.txt = o.type
        o.cb = "Presence"
        self.put(o)

    def resume(self):
        """ method called when resuming the bot. """
        pass

    def say(self, jid, txt, type="chat"):
        """ say test to xmpp user. """
        import sleekxmpp
        logging.warn("> %s %s %s" % (jid, type, txt))
        try:
            sleekxmpp.jid.JID(jid)
        except sleekxmpp.jid.InvalidJID:
            logging.warn("# wrong jid %s" % jid)
            return
        if self.cfg.user in jid:
            logging.warn("# not writing to self.")
            return
        if jid in self.channels:
            type = "groupchat"
        if type == "groupchat":
            jid = stripped(jid)
        self.client.send_message(mto=jid,
                                 mbody=txt,
                                 mtype=type)
         
    def session_start(self, data):
        """ send a presence on startup. """
        logging.info("# session start %s" % data)
        self.client.send_presence()
        self.client.get_roster()

    def sleek(self):
        """ server function of the xmpp bot. """
        self._connected.wait()
        if "client" in self and self.client:
            try:
                self.client.process(block=True)
            except Exception as ex:
                logging.error(get_exception())

    def stop(self):
        """ stop the xmpp bot. """
        if "client" in self and self.client:
            self.client.disconnect()
        super().stop()

    def start(self, *args, **kwargs):
        """ start the xmpp bot. """
        self.connect(self.cfg.user)
        launcher.launch(self.sleek)
        super().start(*args, **kwargs)
