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
"""Aliases for the tako shell."""

import os
import sys
import shlex
import inspect
import pathlib
import builtins

import takoshell.environ

from collections.abc import MutableMapping, Iterable, Sequence
from argparse import ArgumentParser

from takoshell.dirstack import cd, pushd, popd, dirs
from takoshell.jobs import jobs, fg, bg, clean_jobs, disown
from takoshell.coreutils import _which, _echo, _umask
from takoshell.completers._aliases import completer_alias



class Aliases(MutableMapping):
    """Represents a location to hold and look up aliases."""

    def __init__(self, *args, **kwargs):
        self._raw = {}
        self.update(*args, **kwargs)

    def get(self, key, default=None):
        """Returns the (possibly modified) value. If the key is not present,
        then `default` is returned.
        If the value is callable, it is returned without modification. If it
        is an iterable of strings it will be evaluated recursively to expand
        other aliases, resulting in a new list or a "partially applied"
        callable.
        """
        val = self._raw.get(key)
        if val is None:
            return default
        elif isinstance(val, Iterable) or callable(val):
            return self.eval_alias(val, seen_tokens={key})
        else:
            msg = 'alias of {!r} has an inappropriate type: {!r}'
            raise TypeError(msg.format(key, val))

    def eval_alias(self, value, seen_tokens=frozenset(), acc_args=()):
        """
        "Evaluates" the alias `value`, by recursively looking up the leftmost
        token and "expanding" if it's also an alias.

        A value like ["cmd", "arg"] might transform like this:
        > ["cmd", "arg"] -> ["ls", "-al", "arg"] -> callable()
        where `cmd=ls -al` and `ls` is an alias with its value being a
        callable.  The resulting callable will be "partially applied" with
        ["-al", "arg"].
        """
        # Beware of mutability: default values for keyword args are evaluated
        # only once.
        if callable(value):
            if acc_args:  # Partial application
                def _alias(args, stdin=None):
                    args = list(acc_args) + args
                    return value(args, stdin=stdin)
                return _alias
            else:
                return value
        else:
            expand_path = builtins.__tako_expand_path__
            token, *rest = map(expand_path, value)
            if token in seen_tokens or token not in self._raw:
                # ^ Making sure things like `egrep=egrep --color=auto` works,
                # and that `l` evals to `ls --color=auto -CF` if `l=ls -CF`
                # and `ls=ls --color=auto`
                rtn = [token]
                rtn.extend(rest)
                rtn.extend(acc_args)
                return rtn
            else:
                seen_tokens = seen_tokens | {token}
                acc_args = rest + list(acc_args)
                return self.eval_alias(self._raw[token], seen_tokens, acc_args)

    def expand_alias(self, line):
        """Expands any aliases present in line if alias does not point to a
        builtin function and if alias is only a single command.
        """
        word = line.split(' ', 1)[0]
        if word in builtins.__tako_env__['TAKO_SETTINGS'].aliases and isinstance(self.get(word), Sequence):
            word_idx = line.find(word)
            expansion = ' '.join(self.get(word))
            line = line[:word_idx] + expansion + line[word_idx+len(word):]
        return line

    #
    # Mutable mapping interface
    #

    def __getitem__(self, key):
        return self._raw[key]

    def __setitem__(self, key, val):
        if isinstance(val, str):
            self._raw[key] = shlex.split(val)
        else:
            self._raw[key] = val

    def __delitem__(self, key):
        del self._raw[key]

    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).items():
            self[key] = val

    def __iter__(self):
        yield from self._raw

    def __len__(self):
        return len(self._raw)

    def __str__(self):
        return str(self._raw)

    def __repr__(self):
        return '{0}.{1}({2})'.format(self.__class__.__module__,
                                     self.__class__.__name__, self._raw)

    def _repr_pretty_(self, p, cycle):
        name = '{0}.{1}'.format(self.__class__.__module__,
                                self.__class__.__name__)
        with p.group(0, name + '(', ')'):
            if cycle:
                p.text('...')
            elif len(self):
                p.break_()
                p.pretty(dict(self))



def exit(args, stdin=None):  # pylint:disable=redefined-builtin,W0622
    """Sends signal to exit shell."""
    if not clean_jobs():
        # Do not exit if jobs not cleaned up
        return None, None

    builtins.__tako_exit__ = True
    print()  # gimme a newline
    return None, None


def source_alias(args, stdin=None):
    """Executes the contents of the provided files in the current context.
    If sourced file isn't found in cwd, search for file along $PATH to source
    instead"""
    for fname in args:
        if not os.path.isfile(fname):
            fname = takoshell.environ.locate_binary(fname)
        with open(fname, 'r') as fp:
            src = fp.read()
        if not src.endswith('\n'):
            src += '\n'
        builtins.execx(src, 'exec', builtins.__tako_ctx__)


def xexec(args, stdin=None):
    """exec [-h|--help] command [args...]

    exec (also aliased as xexec) uses the os.execvpe() function to
    replace the tako process with the specified program. This provides
    the functionality of the bash 'exec' builtin::

        >>> exec bash -l -i
        bash $

    The '-h' and '--help' options print this message and exit.

    Notes
    -----
    This command **is not** the same as the Python builtin function
    exec(). That function is for running Python code. This command,
    which shares the same name as the sh-lang statement, is for launching
    a command directly in the same process. In the event of a name conflict,
    please use the xexec command directly or dive into subprocess mode
    explicitly with ![exec command]. For more details, please see
    http://xon.sh/faq.html#exec.
    """
    if len(args) == 0:
        return (None, 'tako: exec: no args specified\n', 1)
    elif args[0] == '-h' or args[0] == '--help':
        return inspect.getdoc(xexec)
    else:
        env = builtins.__tako_env__
        denv = env.detype()
        try:
            os.execvpe(args[0], args, denv)
        except FileNotFoundError as e:
            return (None, 'tako: exec: file not found: {}: {}'
                          '\n'.format(e.args[1], args[0]), 1)


def which(args, stdin=None, stdout=None, stderr=None):
    """
    Checks if each arguments is a tako aliases, then if it's an executable,
    then finally return an error code equal to the number of misses.
    If '-a' flag is passed, run both to return both `tako` match and
    `which` match.
    """
    desc = "Parses arguments to which wrapper"
    parser = ArgumentParser('which', description=desc)
    parser.add_argument('args', type=str, nargs='+',
                        help='The executables or aliases to search for')
    parser.add_argument('-a','--all', action='store_true', dest='all',
                        help='Show all matches in $PATH and takoshell.aliases')
    parser.add_argument('-s', '--skip-alias', action='store_true',
                        help='Do not search in takoshell.aliases', dest='skip')
    parser.add_argument('-V', '--version', action='version',
                        version='{}'.format(_which.__version__),
                        help='Display the version of the python which module '
                        'used by tako')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='Print out how matches were located and show '
                        'near misses on stderr')
    parser.add_argument('-p', '--plain', action='store_true', dest='plain',
                        help='Do not display alias expansions or location of '
                             'where binaries are found. This is the '
                             'default behavior, but the option can be used to '
                             'override the --verbose option')
    if len(args) == 0:
        parser.print_usage(file=stderr)
        return -1
    pargs = parser.parse_args(args)

    if pargs.all:
        pargs.verbose = True

    exts = None

    failures = []
    settings = builtins.__tako_env__['TAKO_SETTINGS']
    aliases = settings.aliases
    for arg in pargs.args:
        nmatches = 0
        # skip alias check if user asks to skip
        if (arg in aliases and not pargs.skip):
            if pargs.plain or not pargs.verbose:
                if isinstance(aliases[arg], list):
                    print(' '.join(aliases[arg]), file=stdout)
                else:
                    print(arg, file=stdout)
            else:
                print("$TAKO_SETTINGS.aliases['{}'] = {}".format(arg, aliases[arg]), file=stdout)
            nmatches += 1
            if not pargs.all:
                continue
        else:
            for plugin in settings.plugins:
                local_aliases = settings.plugins[plugin].aliases
                if arg in local_aliases and not pargs.skip:
                    if pargs.plain or not pargs.verbose:
                        if isinstance(local_aliases[arg], list):
                            print(' '.join(local_aliases[arg]), file=stdout)
                        else:
                            print(arg, file=stdout)
                    else:
                        print("$TAKO_SETTINGS.plugins.{}.aliases[{}] = {}".format(plugin.lower(), repr(arg), local_aliases[arg]), file=stdout)
                    nmatches += 1
                    if not pargs.all:
                        continue
        # which.whichgen gives the nicest 'verbose' output if PATH is taken
        # from os.environ so we temporarily override it with
        # __xosnh_env__['PATH']
        original_os_path = os.environ['PATH']
        os.environ['PATH'] = builtins.__tako_env__.detype()['PATH']
        matches = _which.whichgen(arg, exts=exts, verbose=pargs.verbose)
        for abs_name, from_where in matches:
            if pargs.plain or not pargs.verbose:
                print(abs_name, file=stdout)
            else:
                print('{} ({})'.format(abs_name, from_where), file=stdout)
            nmatches += 1
            if not pargs.all:
                break
        os.environ['PATH'] = original_os_path
        if not nmatches:
            failures.append(arg)
    if len(failures) == 0:
        return 0
    else:
        print('{} not in $PATH'.format(', '.join(failures)), file=stderr, end='')
        if not pargs.skip:
            print(' or aliases', file=stderr, end='')
        print('', end='\n')
        return len(failures)


def suppress_welcome(args, stdin=None):
    fileloc = os.path.join(builtins.__tako_env__['XDG_CONFIG_HOME'], 'tako', 'suppress_message')
    filedir = os.path.dirname(fileloc)
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    pathlib.Path(fileloc).touch()
    return "Suppressing tako welcome message in the future.\n"


def license(args, stdin=None):
    return open(os.path.join(os.path.dirname(__file__), 'LICENSE')).read()


def showcmd(args, stdin=None):
    """usage: showcmd [-h|--help|cmd args]

    Displays the command and arguments as a list of strings that tako would
    run in subprocess mode. This is useful for determining how tako evaluates
    your commands and arguments prior to running these commands.

    optional arguments:
      -h, --help            show this help message and exit

    example:
      >>> showcmd echo $USER can't hear "the sea"
      ['echo', 'I', "can't", 'hear', 'the sea']
    """
    if len(args) == 0 or (len(args) == 1 and args[0] in {'-h', '--help'}):
        print(showcmd.__doc__.rstrip().replace('\n    ', '\n'))
    else:
        sys.displayhook(args)


default_aliases = {
    'cd': cd,
    'pushd': pushd,
    'popd': popd,
    'dirs': dirs,
    'jobs': jobs,
    'fg': fg,
    'bg': bg,
    'disown': disown,
    'EOF': exit,
    'exit': exit,
    'quit': exit,
    'tako_license': license,
    'xexec': xexec,
    'exec': xexec,
    'source': source_alias,
    'scp-resume': ['rsync', '--partial', '-h', '--progress', '--rsh=ssh'],
    'showcmd': showcmd,
    'ipynb': ['jupyter', 'notebook', '--no-browser'],
    'which': which,
    'completer': completer_alias,
    'grep': ['grep', '--color=auto'],
    'egrep': ['egrep', '--color=auto'],
    'fgrep': ['fgrep', '--color=auto'],
    'ls': ['ls', '--color=auto', '-v'],
    'suppress_tako_welcome_message': suppress_welcome,
    'echo': _echo.echo,
    'umask': _umask.umask,
}
