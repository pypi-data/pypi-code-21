import os
import logging
import shlex
from io import BytesIO
from traceback import format_exc
from .cli import from_argv, cli as _horetu_cli
from ._bind import web_section
from ._util import stream
from .. import exceptions
from ..program import Program
from ..annotations import Port
try:
    from irc.strings import lower
except ImportError:
    pass

logger = logging.getLogger(__name__)

def _irc(program, server, channel, nick, port, start=True, IRCBot=None):
    '''
    :param bool start: Whether to start the bot. The main reason not to is
        for testing.
    :param type IRCBot: IRCBot to subclass. The default is
        :py:class:`irc.bot.SingleServerIRCBot`. The main reason to change it is
        for testing.
    '''
    from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
    if not IRCBot:
        from irc.bot import SingleServerIRCBot as IRCBot

    if not isinstance(program, Program):
        program = Program(program)
    if not nick:
        nick = program.name
    if not (server and channel and nick):
        raise ValueError('You must set the server, channel, and nick.')

    class HoretuBot(IRCBot):
        def on_nicknameinuse(self, c, e):
            c.nick(c.get_nickname() + "_")

        def on_welcome(self, c, e):
            c.join(channel)

        def on_privmsg(self, c, e):
            _respond(program, e.source.nick, c.notice, c.get_nickname(), e.arguments[0])

        def on_pubmsg(self, c, e):
            line = e.arguments[0]
            nickname = c.get_nickname()
            zero = line.lstrip().split()[0]
            mentioned = zero.startswith(nickname)
            if mentioned:
                _respond(program, e.target, c.privmsg, zero, line)

    bot = HoretuBot([(server, port)], nick, nick)
    if start:
        bot.start()
    else:
        return bot

def irc(program, server, channel,
        nick=None, *, port: Port=6667,
        cli=False, only_mentions=False, debug=False):
    '''
    Render a Python function as an IRC bot.

    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface
    :param server: IRC server to connect to
    :param channel: IRC channel to join
    :param nick: IRC handle
    :param int port: IRC server port
    :param bool cli: If True, render a command-line program that starts an IRC
        bot with the configured values as defaults.
    '''
    if cli:
        def wrapper(server=server, channel=channel,
                    nick=nick, *, port: Port=port):
            _irc(program, server, channel, nick, port)
        wrapper.__doc__ = '''
        Run %s as an IRC bot.

        :param server: IRC server to run on
        :param channel: Channel on the IRC server to run on
        :param nick: Nick to connect with
        :param int port: Port on the server to connect to
        ''' % (program.name or 'the program')

        name = program.name if isinstance(program, Program) else None
        _horetu_cli(Program(wrapper, name))
    else:
        _irc(program, server, channel, nick, port)

def _respond(program, target, method, nickname, line):
    def success(x):
        method(target, x.decode('utf-8'))
    def error(x):
        method(target, x.decode('utf-8'))

    class Exit(Exception):
        pass
    def _exit(code=0):
        raise Exit

    out = BytesIO()
    try:
        _horetu_cli(program, argv=[nickname] + shlex.split(line),
                    exit_=_exit, stdout=out, stderr=out)
        success(out.getvalue().decode('utf-8'))
    except Exit:
        pass
    except UnicodeDecodeError:
        error(b'error: Bad bot output encoding')
