# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

# -*- coding: utf-8 -*-
"""The main tako script."""
import os
import sys
import enum
import builtins
from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
from contextlib import contextmanager

from takoshell import __version__
from takoshell.shell import Shell
from takoshell.pretty import pretty
from takoshell.proc import HiddenCompletedCommand
from takoshell.jobs import ignore_sigtstp
from takoshell.events import fire_event
from takoshell.environ import takorc_context
from takoshell.codecache import run_script_with_cache, run_code_with_cache

def path_argument(s):
    """Return a path only if the path is actually legal

    This is very similar to argparse.FileType, except that it doesn't return
    an open file handle, but rather simply validates the path."""

    s = os.path.abspath(os.path.expanduser(s))
    if not os.path.isfile(s):
        raise ArgumentTypeError('"%s" must be a valid path to a file' % s)
    return s


parser = ArgumentParser(description='tako', add_help=False)
parser.add_argument('-h', '--help',
                    dest='help',
                    action='store_true',
                    default=False,
                    help='show help and exit')
parser.add_argument('-V', '--version',
                    dest='version',
                    action='store_true',
                    default=False,
                    help='show version information and exit')
parser.add_argument('-c',
                    help="Run a single command and exit",
                    dest='command',
                    required=False,
                    default=None)
parser.add_argument('-i', '--interactive',
                    help='force running in interactive mode',
                    dest='force_interactive',
                    action='store_true',
                    default=False)
parser.add_argument('-l', '--login',
                    help='run as a login shell',
                    dest='login',
                    action='store_true',
                    default=False)
parser.add_argument('--no-script-cache',
                    help="Do not cache scripts as they are run",
                    dest='scriptcache',
                    action='store_false',
                    default=True)
parser.add_argument('--cache-everything',
                    help="Use a cache, even for interactive commands",
                    dest='cacheall',
                    action='store_true',
                    default=False)
parser.add_argument('-D',
                    dest='defines',
                    help='define an environment variable, in the form of '
                         '-DNAME=VAL. May be used many times.',
                    metavar='ITEM',
                    action='append',
                    default=None)
parser.add_argument('file',
                    metavar='script-file',
                    help='If present, execute the script in script-file'
                         ' and exit',
                    nargs='?',
                    default=None)
parser.add_argument('-s', '--suppress-license-info',
                    dest='suppress_license_info',
                    action='store_true',
                    help='If present, do not print license information')
parser.add_argument('args',
                    metavar='args',
                    help='Additional arguments to the script specified '
                         'by script-file',
                    nargs=REMAINDER,
                    default=[])


def _pprint_displayhook(value):
    if value is None:
        return
    builtins._ = None  # Set '_' to None to avoid recursion
    if isinstance(value, HiddenCompletedCommand):
        builtins._ = value
        return
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    if settings.pretty_print_results:
        printed_val = pretty(value)
    else:
        printed_val = repr(value)
    print(printed_val)  # black & white case
    builtins._ = value


class TakoMode(enum.Enum):
    single_command = 0
    script_from_file = 1
    script_from_stdin = 2
    interactive = 3


def premain(argv=None):
    """Setup for main tako entry point, returns parsed arguments."""
    if argv is None:
        argv = sys.argv[1:]
    # TODO: set process title with prctl
    builtins.__tako_ctx__ = {}
    args = parser.parse_args(argv)
    if args.help:
        parser.print_help()
        parser.exit()
    if args.version:
        version = '/'.join(('tako', __version__))
        print(version)
        parser.exit()
    shell_kwargs = {'headless': False,
                    'completer': False,
                    'login': False,
                    'scriptcache': args.scriptcache,
                    'cacheall': args.cacheall,
                    'ctx': builtins.__tako_ctx__}
    if args.login:
        shell_kwargs['login'] = True
    setattr(sys, 'displayhook', _pprint_displayhook)
    if args.command is not None:
        args.mode = TakoMode.single_command
        shell_kwargs['headless'] = True
    elif args.file is not None:
        args.mode = TakoMode.script_from_file
        shell_kwargs['headless'] = True
    elif not sys.stdin.isatty() and not args.force_interactive:
        args.mode = TakoMode.script_from_stdin
        shell_kwargs['headless'] = True
    else:
        args.mode = TakoMode.interactive
        shell_kwargs['completer'] = True
        shell_kwargs['login'] = True
    from takoshell import imphooks
    shell = Shell(**shell_kwargs)
    env = builtins.__tako_env__
    takorc_context('config.tako', execer=shell.execer, initial=shell.ctx)
    env['TAKO_LOGIN'] = shell_kwargs['login']
    if args.defines is not None:
        env.update([x.split('=', 1) for x in args.defines])
    env['TAKO_INTERACTIVE'] = args.force_interactive
    return args

WELCOME_MESSAGE = """\
 ____
( oo )
_||||_

This is the Tako Shell, version %s.
tako is free/libre software, available under the terms of the GNU General
Public License version 3.  To view the full license, run the "tako_license"
command.  The source code for tako is available at https://takoshell.org

To suppress this message permanently, run the following command:
    $ suppress_tako_welcome_message
"""

def main(argv=None):
    """Main entry point for tako cli."""
    if argv is None:
        argv = sys.argv[1:]
    args = premain(argv)
    fire_event('on_load')
    env = builtins.__tako_env__
    shell = builtins.__tako_shell__
    never_print = os.path.isfile(os.path.join(env['XDG_CONFIG_HOME'], 'tako', 'suppress_message'))
    done = False
    if not args.suppress_license_info and not never_print:
        print(WELCOME_MESSAGE % __version__, file=sys.stderr)
    if args.mode == TakoMode.single_command:
        # run a single command and exit
        run_code_with_cache(args.command.lstrip(), shell.execer, mode='single')
        done = True
    elif args.mode == TakoMode.script_from_file:
        # run a script contained in a file
        path = os.path.abspath(os.path.expanduser(args.file))
        if os.path.isfile(path):
            sys.argv = [args.file] + args.args
            env['ARGS'] = sys.argv[:]
            env['TAKO_SOURCE'] = path
            run_script_with_cache(args.file, shell.execer, glb=shell.ctx,
                                  loc=None, mode='exec')
        else:
            print('tako: {0}: No such file or directory.'.format(args.file))
        done = True
    elif args.mode == TakoMode.script_from_stdin:
        # run a script given on stdin
        code = sys.stdin.read()
        run_code_with_cache(code, shell.execer, glb=shell.ctx, loc=None,
                            mode='exec')
        done = True
    if args.force_interactive or not done:
        # otherwise, enter the shell
        env['TAKO_INTERACTIVE'] = True
        ignore_sigtstp()
        shell.cmdloop()
    fire_event('on_exit')
    postmain(args)


def postmain(args=None):
    """Teardown for main tako entry point, accepts parsed arguments."""
    del builtins.__tako_shell__


@contextmanager
def main_context(argv=None):
    """Generator that runs pre- and post-main() functions. This has two iterations.
    The first yields the shell. The second returns None but cleans
    up the shell.
    """
    args = premain(argv)
    yield builtins.__tako_shell__
    postmain(args)


if __name__ == '__main__':
    main()
