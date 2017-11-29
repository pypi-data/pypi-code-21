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
"""Environment for the tako shell."""
import os
import sys
import locale
import builtins
from contextlib import contextmanager
from pprint import pformat
import re
import string
from warnings import warn
from collections import (MutableMapping, MutableSequence, MutableSet,
    namedtuple)

from takoshell import __version__ as TAKO_VERSION
from takoshell.codecache import run_script_with_cache
from takoshell.dirstack import _get_cwd
from takoshell.platform import PATH_DEFAULT
from takoshell.tools import (always_true, always_false, ensure_string, is_env_path,
                        str_to_env_path, env_path_to_str, DefaultNotGiven,
                        print_exception, EnvPath, executables_in, COLORS_256,
                        COLORS_TAKO)
import takoshell.settings


LOCALE_CATS = {
    'LC_CTYPE': locale.LC_CTYPE,
    'LC_COLLATE': locale.LC_COLLATE,
    'LC_NUMERIC': locale.LC_NUMERIC,
    'LC_MONETARY': locale.LC_MONETARY,
    'LC_TIME': locale.LC_TIME,
}
if hasattr(locale, 'LC_MESSAGES'):
    LOCALE_CATS['LC_MESSAGES'] = locale.LC_MESSAGES


def locale_convert(key):
    """Creates a converter for a locale key."""
    def lc_converter(val):
        try:
            locale.setlocale(LOCALE_CATS[key], val)
            val = locale.setlocale(LOCALE_CATS[key])
        except (locale.Error, KeyError):
            warn('Failed to set locale {0!r} to {1!r}'.format(key, val),
                 RuntimeWarning)
        return val
    return lc_converter


Ensurer = namedtuple('Ensurer', ['validate', 'convert', 'detype'])
Ensurer.__doc__ = """Named tuples whose elements are functions that
represent environment variable validation, conversion, detyping.
"""

DEFAULT_ENSURERS = {
    re.compile('\w*DIRS$'): (is_env_path, str_to_env_path, env_path_to_str),
    'LC_COLLATE': (always_false, locale_convert('LC_COLLATE'), ensure_string),
    'LC_CTYPE': (always_false, locale_convert('LC_CTYPE'), ensure_string),
    'LC_MESSAGES': (always_false, locale_convert('LC_MESSAGES'), ensure_string),
    'LC_MONETARY': (always_false, locale_convert('LC_MONETARY'), ensure_string),
    'LC_NUMERIC': (always_false, locale_convert('LC_NUMERIC'), ensure_string),
    'LC_TIME': (always_false, locale_convert('LC_TIME'), ensure_string),
    re.compile('\w*PATH$'): (is_env_path, str_to_env_path, env_path_to_str),
}



# Default values should generally be immutable, that way if a user wants
# to set them they have to do a copy and write them to the environment.
# try to keep this sorted.
DEFAULT_VALUES = {
    'CDPATH': (),
    'LC_CTYPE': locale.setlocale(locale.LC_CTYPE),
    'LC_COLLATE': locale.setlocale(locale.LC_COLLATE),
    'LC_TIME': locale.setlocale(locale.LC_TIME),
    'LC_MONETARY': locale.setlocale(locale.LC_MONETARY),
    'LC_NUMERIC': locale.setlocale(locale.LC_NUMERIC),
    'PATH': PATH_DEFAULT,
    'XDG_CONFIG_HOME': os.path.expanduser(os.path.join('~', '.config')),
    'XDG_DATA_HOME': os.path.expanduser(os.path.join('~', '.local', 'share')),
}
if hasattr(locale, 'LC_MESSAGES'):
    DEFAULT_VALUES['LC_MESSAGES'] = locale.setlocale(locale.LC_MESSAGES)

VarDocs = namedtuple('VarDocs', ['docstr', 'configurable', 'default',
                                 'store_as_str'])
VarDocs.__doc__ = """Named tuple for environment variable documentation

Parameters
----------
docstr : str
   The environment variable docstring.
configurable : bool, optional
    Flag for whether the environment variable is configurable or not.
default : str, optional
    Custom docstring for the default value for complex defaults.
    Is this is DefaultNotGiven, then the default will be looked up
    from DEFAULT_VALUES and converted to a str.
store_as_str : bool, optional
    Flag for whether the environment variable should be stored as a
    string. This is used when persisting a variable that is not JSON
    serializable to the config file. For example, sets, frozensets, and
    potentially other non-trivial data types. default, False.
"""
# iterates from back
VarDocs.__new__.__defaults__ = (True, DefaultNotGiven, False)

# Please keep the following in alphabetic order - scopatz
DEFAULT_DOCS = {
    'CDPATH': VarDocs(
        'A list of paths to be used as roots for a cd, breaking compatibility '
        'with Bash, tako always prefer an existing relative path.'),
    'OLDPWD': VarDocs('Used to represent a previous present working directory.',
        configurable=False),
    'PATH': VarDocs(
        'List of strings representing where to look for executables.'),
    'TERM': VarDocs(
        'TERM is sometimes set by the terminal emulator. This is used (when '
        "valid) to determine whether or not to set the title. Users shouldn't "
        "need to set this themselves. Note that this variable should be set as "
        "early as possible in order to ensure it is effective. Here are a few "
        "options:\n\n"
        "* Set this from the program that launches takoshell. On POSIX systems, \n"
        "  this can be performed by using env, e.g. \n"
        "  '/usr/bin/env TERM=xterm-color tako' or similar.\n"
        "* From the tako command line, namely 'tako -DTERM=xterm-color'.\n"
        "* In the config file with '{\"env\": {\"TERM\": \"xterm-color\"}}'.\n"
        "* Lastly, in takorc with '$TERM'\n\n"
        "Ideally, your terminal emulator will set this correctly but that does "
        "not always happen.", configurable=False),
    'XDG_CONFIG_HOME': VarDocs(
        'Open desktop standard configuration home dir. This is the same '
        'default as used in the standard.', configurable=False,
        default="'~/.config'"),
    'XDG_DATA_HOME': VarDocs(
        'Open desktop standard data home dir. This is the same default as '
        'used in the standard.', default="'~/.local/share'"),
}

#
# actual environment
#

class Env(MutableMapping):
    """A tako environment, whose variables have limited typing
    (unlike BASH). Most variables are, by default, strings (like BASH).
    However, the following rules also apply based on variable-name:

    * PATH: any variable whose name ends in PATH is a list of strings.
    * LC_* (locale categories): locale catergory names get/set the Python
      locale via locale.getlocale() and locale.setlocale() functions.

    An Env instance may be converted to an untyped version suitable for
    use in a subprocess.
    """

    _arg_regex = re.compile(r'(\d+)')

    def __init__(self, *args, **kwargs):
        """If no initial environment is given, os.environ is used."""
        self._d = {}
        self._orig_env = None
        self._ensurers = {k: Ensurer(*v) for k, v in DEFAULT_ENSURERS.items()}
        self._defaults = DEFAULT_VALUES
        self._docs = DEFAULT_DOCS
        if len(args) == 0 and len(kwargs) == 0:
            args = (os.environ, )
        for key, val in dict(*args, **kwargs).items():
            self[key] = val
        if 'PATH' not in self._d:
            # this is here so the PATH is accessible to subprocs and so that
            # it can be modified in-place in the takorc file
            self._d['PATH'] = EnvPath(PATH_DEFAULT)
        self._detyped = None

    @staticmethod
    def detypeable(val):
        return not (callable(val) or isinstance(val, MutableMapping))

    def detype(self):
        if self._detyped is not None:
            return self._detyped
        ctx = {}
        for key, val in self._d.items():
            if key == 'TAKO_SETTINGS':
                continue
            if not self.detypeable(val):
                continue
            if not isinstance(key, str):
                key = str(key)
            ensurer = self.get_ensurer(key)
            val = ensurer.detype(val)
            ctx[key] = val
        self._detyped = ctx
        return ctx

    def replace_env(self):
        """Replaces the contents of os.environ with a detyped version
        of the tako environement.
        """
        if self._orig_env is None:
            self._orig_env = dict(os.environ)
        os.environ.clear()
        os.environ.update(self.detype())

    def undo_replace_env(self):
        """Replaces the contents of os.environ with a detyped version
        of the tako environement.
        """
        if self._orig_env is not None:
            os.environ.clear()
            os.environ.update(self._orig_env)
            self._orig_env = None

    def get_ensurer(self, key,
                    default=Ensurer(always_true, None, ensure_string)):
        """Gets an ensurer for the given key."""
        if key in self._ensurers:
            return self._ensurers[key]
        for k, ensurer in self._ensurers.items():
            if isinstance(k, str):
                continue
            if k.match(key) is not None:
                break
        else:
            ensurer = default
        self._ensurers[key] = ensurer
        return ensurer

    def get_docs(self, key, default=VarDocs('<no documentation>')):
        """Gets the documentation for the environment variable."""
        vd = self._docs.get(key, None)
        if vd is None:
            return default
        if vd.default is DefaultNotGiven:
            dval = pformat(self._defaults.get(key, '<default not set>'))
            vd = vd._replace(default=dval)
            self._docs[key] = vd
        return vd

    def is_manually_set(self, varname):
        """
        Checks if an environment variable has been manually set.
        """
        return varname in self._d

    @contextmanager
    def tempset(self, other=None, **kwargs):
        """Provides a context manager for temporarily swapping out certain
        environment variables with other values. On exit from the context
        manager, the original values are restored.
        """
        old = {}
        # single positional argument should be a dict-like object
        if other is not None:
            for k, v in other.items():
                old[k] = self.get(k, NotImplemented)
                self[k] = v
        # kwargs could also have been sent in
        for k, v in kwargs.items():
            old[k] = self.get(k, NotImplemented)
            self[k] = v

        yield self
        # restore the values
        for k, v in old.items():
            if v is NotImplemented:
                del self[k]
            else:
                self[k] = v


    #
    # Mutable mapping interface
    #

    def __getitem__(self, key):
        if key is Ellipsis:
            return self
        m = self._arg_regex.match(key)
        if (m is not None) and (key not in self._d) and ('ARGS' in self._d):
            args = self._d['ARGS']
            ix = int(m.group(1))
            if ix >= len(args):
                e = "Not enough arguments given to access ${0}."
                raise KeyError(e.format(ix))
            val = self._d['ARGS'][ix]
        elif key in self._d:
            val = self._d[key]
        elif key in self._defaults:
            val = self._defaults[key]
        else:
            e = "Unknown environment variable: ${}"
            raise KeyError(e.format(key))
        if isinstance(val, (MutableSet, MutableSequence, MutableMapping)):
            self._detyped = None
        return val

    def __setitem__(self, key, val):
        ensurer = self.get_ensurer(key)
        if not ensurer.validate(val):
            val = ensurer.convert(val)
        self._d[key] = val
        if self.detypeable(val):
            self._detyped = None
            if ('TAKO_SETTINGS' in self and
                    'UPDATE_OS_ENVIRON' in self['TAKO_SETTINGS'] and
                    self['TAKO_SETTINGS'].update_os_environ):
                if self._orig_env is None:
                    self.replace_env()
                else:
                    os.environ[key] = ensurer.detype(val)

    def __delitem__(self, key):
        val = self._d.pop(key)
        if self.detypeable(val):
            self._detyped = None
            if self['TAKO_SETTINGS'].update_os_environ and key in os.environ:
                del os.environ[key]

    def get(self, key, default=None):
        """The environment will look up default values from its own defaults if a
        default is not given here.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __iter__(self):
        yield from (set(self._d) | set(self._defaults))

    def __len__(self):
        return len(self._d)

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return '{0}.{1}(...)'.format(self.__class__.__module__,
                                     self.__class__.__name__, self._d)

    def _repr_pretty_(self, p, cycle):
        name = '{0}.{1}'.format(self.__class__.__module__,
                                self.__class__.__name__)
        with p.group(0, name + '(', ')'):
            if cycle:
                p.text('...')
            elif len(self):
                p.break_()
                p.pretty(dict(self))


def _yield_executables(directory, name):
    for x in executables_in(directory):
        if x == name:
            yield os.path.join(directory, name)
            return


def locate_binary(name):
    """Locates an executable on the file system."""
    if os.path.isfile(name) and name != os.path.basename(name):
        return name
    cc = builtins.__tako_commands_cache__
    if name in cc:
        # can be lazy here since we know name is already available
        return cc.lazyget(name)[0]


_FORMATTER = string.Formatter()


def format_prompt(template, prompt_fields=None, prompt_colors=None, ignore=None):
    """Formats a tako prompt template string."""
    template = template() if callable(template) else template
    fmtter = builtins.__tako_env__['TAKO_SETTINGS'].PROMPT_FIELDS
    try:
        included_names = set(i[1] for i in _FORMATTER.parse(template))
    except Exception:
        included_names = set()
    fmt = {}
    if not prompt_colors:
        prompt_colors = {}
    if ignore is None:
        ignore = set()
    try:
        for name in included_names:
            if name is None or name in ignore:
                continue
            if name.startswith('$'):
                v = builtins.__tako_env__[name[1:]]
            elif name in fmtter:
                v = fmtter[name]
            elif name in prompt_colors:
                v = prompt_colors[name]
            else:
                v = '{%s}' % name
            if callable(v):
                v = v()
            v = '' if v is None else str(v)
            v = format_prompt(v, prompt_fields, prompt_colors, ignore | {name})
            fmt[name] = v
    except:
        print("tako: Function %s raised an exception when formatting prompt." % name, file=sys.stderr)
        print_exception()
        return template
    try:
        return template.format(**fmt)
    except Exception:
        return template


RE_HIDDEN = re.compile('\001.*?\002')

def multiline_prompt():
    """Returns the filler text for the prompt in multiline scenarios."""
    env = builtins.__tako_env__
    settings = env.get('TAKO_SETTINGS')
    curr = settings.prompt
    colors = COLORS_256 if '256color' in env.get('TERM', '') else COLORS_TAKO
    curr = format_prompt(curr, prompt_colors=colors)
    line = curr.rsplit('\n', 1)[1] if '\n' in curr else curr
    line = RE_HIDDEN.sub('', line)  # gets rid of colors
    # most prompts end in whitespace, head is the part before that.
    head = line.rstrip()
    headlen = len(head)
    # tail is the trailing whitespace
    tail = line if headlen == 0 else line.rsplit(head[-1], 1)[1]
    # now to constuct the actual string
    dots = settings.multiline_prompt
    dots = dots() if callable(dots) else dots
    if dots is None or len(dots) == 0:
        return ''
    return (dots * (headlen // len(dots))) + dots[:headlen % len(dots)] + tail


BASE_ENV = {
    'TAKO_VERSION': TAKO_VERSION,
    'TAKO_SETTINGS': takoshell.settings.tako_settings,
}


def takorc_context(rcfile=None, execer=None, initial=None, absolute=False):
    """Attempts to read in takorc file, and return the contents."""
    if rcfile is None:
        rcfile = 'preload.tako'
    if not absolute:
        rcfile = os.path.join(takoshell.settings.tako_settings.config_dir, rcfile)
    if initial is None:
        env = {}
    else:
        env = initial
    if execer is None or not os.path.isfile(rcfile):
        return env
    try:
        run_script_with_cache(rcfile, execer, env)
    except SyntaxError as err:
        msg = 'syntax error in tako run control file {0!r}: {1!s}'
        warn(msg.format(rcfile, err), RuntimeWarning)
        return env
    except Exception as err:
        msg = 'error running tako run control file {0!r}: {1!s}'
        warn(msg.format(rcfile, err), RuntimeWarning)
        return env
    return env


def default_env(env=None, login=True):
    """Constructs a default tako environment."""
    # in order of increasing precedence
    ctx = dict(BASE_ENV)
    ctx.update(os.environ)
    ctx['PWD'] = _get_cwd() or ''

    # finalize env
    if env is not None:
        ctx.update(env)
    return ctx
