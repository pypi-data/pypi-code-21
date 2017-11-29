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
"""The base class for tako shell"""
import os
import sys
import builtins

from takoshell.tools import (TakoError, print_exception, check_for_partial_string,
                        COLORS_256, COLORS_TAKO)
from takoshell.codecache import (should_use_cache, code_cache_name,
                             code_cache_check, get_cache_filename,
                             update_cache, run_compiled_code)
from takoshell.completer import Completer
from takoshell.environ import multiline_prompt, format_prompt

from takoshell.events import fire_event


class BaseShell(object):
    """The tako shell."""

    def __init__(self, execer, ctx, **kwargs):
        super().__init__()
        self.execer = execer
        self.ctx = ctx
        self.completer = Completer() if kwargs.get('completer', True) else None
        self.buffer = []
        self.need_more_lines = False
        self.mlprompt = None
        self.styler = None

    def emptyline(self):
        """Called when an empty line has been entered."""
        self.need_more_lines = False
        self.default('')

    def singleline(self, **kwargs):
        """Reads a single line of input from the shell."""
        msg = '{0} has not implemented singleline().'
        raise RuntimeError(msg.format(self.__class__.__name__))

    def precmd(self, line):
        """Called just before execution of line."""
        return line if self.need_more_lines else line.lstrip()

    def default(self, line):
        """Implements code execution."""
        line = line if line.endswith('\n') else line + '\n'
        src, code = self.push(line)
        if code is None:
            return
        try:
            run_compiled_code(code, self.ctx, None, 'single')
        except TakoError as e:
            print(e.args[0], file=sys.stderr)
        except Exception:  # pylint: disable=broad-except
            print_exception()
        self._fix_cwd()
        if builtins.__tako_exit__:  # pylint: disable=no-member
            return True

    def _fix_cwd(self):
        """Check if the cwd changed out from under us"""
        try:
            cwd = os.getcwd()
        except FileNotFoundError:
            # PWD was deleted?
            print('tako: error: working directory does not exist.  moving up to existing directory',
                  file=sys.stderr)
            cwd = os.path.realpath(builtins.__tako_env__['PWD'])
            while not os.path.isdir(cwd) and cwd != '':
                cwd = os.path.dirname(cwd)
            if cwd == '':
                cwd = '/'
            os.chdir(cwd)
        if os.path.realpath(cwd) != os.path.realpath(builtins.__tako_env__.get('PWD')):
            old = builtins.__tako_env__.get('PWD')             # working directory changed without updating $PWD
            builtins.__tako_env__['PWD'] = cwd             # track it now
            if old is not None:
                builtins.__tako_env__['OLDPWD'] = old      # and update $OLDPWD like dirstack.
            fire_event('on_chdir', cwd, old)

    def push(self, line):
        """Pushes a line onto the buffer and compiles the code in a way that
        enables multiline input.
        """
        code = None
        self.buffer.append(line)
        if self.need_more_lines and line.strip():
            return None, code
        src = ''.join(self.buffer)
        _cache = should_use_cache(self.execer, 'single')
        if _cache:
            codefname = code_cache_name(src)
            cachefname = get_cache_filename(codefname, code=True)
            usecache, code = code_cache_check(cachefname)
            if usecache:
                self.reset_buffer()
                return src, code
        try:
            code = self.execer.compile(src,
                                       mode='single',
                                       glbs=self.ctx,
                                       locs=None)
            if _cache:
                update_cache(code, cachefname)
            self.reset_buffer()
        except SyntaxError:
            partial_string_info = check_for_partial_string(src)
            in_partial_string = (partial_string_info[0] is not None and
                                 partial_string_info[1] is None)
            if ((line == '\n' and not in_partial_string)):
                self.reset_buffer()
                print_exception()
                return src, None
            self.need_more_lines = True
        except Exception:  # pylint: disable=broad-except
            self.reset_buffer()
            print_exception()
            return src, None
        return src, code

    def reset_buffer(self):
        """Resets the line buffer."""
        self.buffer.clear()
        self.need_more_lines = False
        self.mlprompt = None

    def settitle(self):
        """Sets terminal title."""
        env = builtins.__tako_env__  # pylint: disable=no-member
        settings = env['TAKO_SETTINGS']
        term = env.get('TERM', None)
        # Shells running in emacs sets TERM to "dumb" or "eterm-color".
        # Do not set title for these to avoid garbled prompt.
        if term in ['dumb', 'eterm-color', 'linux']:
            return
        t = settings.title
        if t is None:
            return
        t = format_prompt(t)
        with open(1, 'wb', closefd=False) as f:
            # prevent tako from answering interative questions
            # on the next command by writing the title
            f.write("\x1b]0;{0}\x07".format(t).encode())
            f.flush()

    @property
    def prompt(self):
        """Obtains the current prompt string."""
        if self.need_more_lines:
            if self.mlprompt is None:
                try:
                    self.mlprompt = multiline_prompt()
                except Exception:  # pylint: disable=broad-except
                    print_exception()
                    self.mlprompt = '<multiline prompt error> '
            return self.mlprompt
        env = builtins.__tako_env__  # pylint: disable=no-member
        p = env['TAKO_SETTINGS'].prompt
        colors = COLORS_256 if '256color' in env.get('TERM', '') else COLORS_TAKO
        p = format_prompt(p, prompt_colors=colors)
        self.settitle()
        return p
