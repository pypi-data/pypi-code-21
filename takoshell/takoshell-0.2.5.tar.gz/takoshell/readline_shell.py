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
"""The readline based tako shell.

Portions of this code related to initializing the readline library
are included from the IPython project.  The IPython project is:
    * Copyright (c) 2008-2014, IPython Development Team
    * Copyright (c) 2001-2007, Fernando Perez <fernando.perez@colorado.edu>
    * Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
    * Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
"""
import os
import sys
import select
import builtins
import importlib
from cmd import Cmd
from collections import deque

from takoshell.base_shell import BaseShell
from takoshell.tools import print_exception, check_for_partial_string
from takoshell.platform import ON_CYGWIN, ON_DARWIN

readline = None
RL_COMPLETION_SUPPRESS_APPEND = RL_LIB = RL_STATE = None
RL_CAN_RESIZE = False
RL_DONE = None
RL_VARIABLE_VALUE = None
_RL_STATE_DONE = 0x1000000
_RL_STATE_ISEARCH = 0x0000080

def setup_readline():
    """Sets up the readline module and completion suppression, if available."""
    global RL_COMPLETION_SUPPRESS_APPEND, RL_LIB, RL_CAN_RESIZE, RL_STATE, readline
    if RL_COMPLETION_SUPPRESS_APPEND is not None:
        return
    for _rlmod_name in ('gnureadline', 'readline'):
        try:
            readline = importlib.import_module(_rlmod_name)
            sys.modules['readline'] = readline
        except ImportError:
            pass
        else:
            break
    if readline is None:
        print("No readline implementation available.  Skipping setup.")
        return
    import ctypes
    import ctypes.util
    uses_libedit = readline.__doc__ and 'libedit' in readline.__doc__
    readline.set_completer_delims(' \t\n')
    # Cygwin seems to hang indefinitely when querying the readline lib
    if (not ON_CYGWIN) and (not readline.__file__.endswith('.py')):
        RL_LIB = lib = ctypes.cdll.LoadLibrary(readline.__file__)
        try:
            RL_COMPLETION_SUPPRESS_APPEND = ctypes.c_int.in_dll(
                lib, 'rl_completion_suppress_append')
        except ValueError:
            # not all versions of readline have this symbol, ie Macs sometimes
            RL_COMPLETION_SUPPRESS_APPEND = None
        try:
            RL_STATE = ctypes.c_int.in_dll(lib, 'rl_readline_state')
        except:
            pass
        RL_CAN_RESIZE = hasattr(lib, 'rl_reset_screen_size')
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    # reads in history
    hf = settings.history_file
    if os.path.isfile(hf):
        try:
            readline.read_history_file(hf)
        except PermissionError:
            pass
    # sets up IPython-like history matching with up and down
    readline.parse_and_bind('"\e[B": history-search-forward')
    readline.parse_and_bind('"\e[A": history-search-backward')
    # Setup Shift-Tab to indent
    readline.parse_and_bind('"\e[Z": "{0}"'.format(settings.indent))

    # handle tab completion differences found in libedit readline compatibility
    # as discussed at http://stackoverflow.com/a/7116997
    if uses_libedit and ON_DARWIN:
        readline.parse_and_bind("bind ^I rl_complete")
        print('\n'.join(['', "*"*78,
            "libedit detected - readline will not be well behaved, including but not limited to:",
            "   * crashes on tab completion",
            "   * incorrect history navigation",
            "   * corrupting long-lines",
            "   * failure to wrap or indent lines properly",
            "",
            "It is highly recommended that you install gnureadline, which is installable with:",
            "     pip install gnureadline",
            "*"*78]), file=sys.stderr)
    else:
        readline.parse_and_bind("tab: complete")
    # try to load custom user settings
    inputrc_name = os.environ.get('INPUTRC')
    if inputrc_name is None:
        if uses_libedit:
            inputrc_name = '.editrc'
        else:
            inputrc_name = '.inputrc'
        inputrc_name = os.path.join(os.path.expanduser('~'), inputrc_name)
    if not os.path.isfile(inputrc_name):
        inputrc_name = '/etc/inputrc'
    if os.path.isfile(inputrc_name):
        try:
            readline.read_init_file(inputrc_name)
        except Exception:
            # this seems to fail with libedit
            print_exception('tako: could not load readline default init file.')


def teardown_readline():
    """Tears down up the readline module, if available."""
    try:
        import readline
    except (ImportError, TypeError):
        return
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    hs = settings.history_size
    readline.set_history_length(hs)
    hf = settings.history_file
    try:
        readline.write_history_file(hf)
    except PermissionError:
        pass


def fix_readline_state_after_ctrl_c():
    """
    Fix to allow Ctrl-C to exit reverse-i-search.

    Based on code from:
        http://bugs.python.org/file39467/raw_input__workaround_demo.py
    """
    if RL_STATE is None:
        return
    if RL_STATE.value & _RL_STATE_ISEARCH:
        RL_STATE.value &= ~_RL_STATE_ISEARCH
    if not RL_STATE.value & _RL_STATE_DONE:
        RL_STATE.value |= _RL_STATE_DONE


def rl_completion_suppress_append(val=1):
    """Sets the rl_completion_suppress_append varaiable, if possible.
    A value of 1 (default) means to suppress, a value of 0 means to enable.
    """
    if RL_COMPLETION_SUPPRESS_APPEND is None:
        return
    RL_COMPLETION_SUPPRESS_APPEND.value = val


def rl_variable_dumper(readable=True):
    """Dumps the currently set readline variables. If readable is True, then this
    output may be used in an inputrc file.
    """
    RL_LIB.rl_variable_dumper(int(readable))


def rl_variable_value(variable):
    """Returns the currently set value for a readline configuration variable."""
    global RL_VARIABLE_VALUE
    if RL_VARIABLE_VALUE is None:
        import ctypes
        RL_VARIABLE_VALUE = RL_LIB.rl_variable_value
        RL_VARIABLE_VALUE.restype = ctypes.c_char_p
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    enc, errors = settings.encoding, settings.encoding_errors
    if isinstance(variable, str):
        variable = variable.encode(encoding=enc, errors=errors)
    rtn = RL_VARIABLE_VALUE(variable)
    return rtn.decode(encoding=enc, errors=errors)


def _insert_text_func(s, readline):
    """Creates a function to insert text via readline."""
    def inserter():
        readline.insert_text(s)
        readline.redisplay()
    return inserter


DEDENT_TOKENS = frozenset(['raise', 'return', 'pass', 'break', 'continue'])


class ReadlineShell(BaseShell, Cmd):
    """The readline based tako shell."""

    def __init__(self, completekey='tab', stdin=None, stdout=None, **kwargs):
        super().__init__(completekey=completekey,
                         stdin=stdin,
                         stdout=stdout,
                         **kwargs)
        setup_readline()
        self._current_indent = ''
        self._current_prompt = ''
        self._force_hide = None
        self.cmdqueue = deque()

    def __del__(self):
        teardown_readline()

    def singleline(self, store_in_history=True, **kwargs):
        """Reads a single line of input. The store_in_history kwarg
        flags whether the input should be stored in readline's in-memory
        history.
        """
        if not store_in_history:  # store current position to remove it later
            try:
                import readline
            except ImportError:
                store_in_history = True
            pos = readline.get_current_history_length() - 1
        rtn = input(self.prompt)
        if not store_in_history and pos >= 0:
            readline.remove_history_item(pos)
        return rtn

    def parseline(self, line):
        """Overridden to no-op."""
        return '', line, line

    def completedefault(self, text, line, begidx, endidx):
        """Implements tab-completion for text."""
        if self.completer is None:
            return []
        rl_completion_suppress_append()  # this needs to be called each time
        offset = 0
        effective_line = line[:endidx]
        _s, _e, _q = check_for_partial_string(effective_line)
        if _s is not None:
            if _e is not None and ' ' in line[_e:]:
                mline = effective_line.rpartition(' ')[2]
            else:
                mline = effective_line[_s:]
        else:
            mline = effective_line.rpartition(' ')[2]
        offset = len(mline) - len(text)
        comps = self.completer.complete(text, line,
                                        begidx, endidx,
                                        ctx=self.ctx)
        x = [i[offset:] for i in comps[0]]
        return x

    # tab complete on first index too
    completenames = completedefault

    def _load_remaining_input_into_queue(self):
        buf = b''
        while True:
            r, w, x = select.select([self.stdin], [], [], 1e-6)
            if len(r) == 0:
                break
            buf += os.read(self.stdin.fileno(), 1024)
        if len(buf) > 0:
            buf = buf.decode().replace('\r\n', '\n').replace('\r', '\n')
            self.cmdqueue.extend(buf.splitlines(keepends=True))

    def postcmd(self, stop, line):
        """Called just before execution of line. For readline, this handles the
        automatic indentation of code blocks.
        """
        try:
            import readline
        except ImportError:
            return stop
        env = builtins.__tako_env__
        settings = env['TAKO_SETTINGS']
        if self.need_more_lines:
            if len(line.strip()) == 0:
                readline.set_pre_input_hook(None)
                self._current_indent = ''
            elif line.rstrip()[-1] == ':':
                ind = line[:len(line) - len(line.lstrip())]
                ind += settings.indent
                readline.set_pre_input_hook(_insert_text_func(ind, readline))
                self._current_indent = ind
            elif line.split(maxsplit=1)[0] in DEDENT_TOKENS:
                ind = self._current_indent[:-len(settings.indent)]
                readline.set_pre_input_hook(_insert_text_func(ind, readline))
                self._current_indent = ind
            else:
                ind = line[:len(line) - len(line.lstrip())]
                if ind != self._current_indent:
                    insert_func = _insert_text_func(ind, readline)
                    readline.set_pre_input_hook(insert_func)
                    self._current_indent = ind
        else:
            readline.set_pre_input_hook(None)
        return stop

    def _cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        This was forked from Lib/cmd.py from the Python standard library v3.4.3,
        (C) Python Software Foundation, 2015.
        """
        self.preloop()
        env = builtins.__tako_env__
        settings = env['TAKO_SETTINGS']
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
                have_readline = True
            except ImportError:
                have_readline = False
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                line = None
                exec_now = False
                if len(self.cmdqueue) > 0:
                    line = self.cmdqueue.popleft()
                    exec_now = line.endswith('\n')
                if self.use_rawinput and not exec_now:
                    inserter = None if line is None \
                                    else _insert_text_func(line, readline)
                    if inserter is not None:
                        readline.set_pre_input_hook(inserter)
                    try:
                        line = self.singleline()
                    except EOFError:
                        if settings.ignoreEOF:
                            self.stdout.write('Use "exit" to leave the shell.'
                                              '\n')
                            line = ''
                        else:
                            line = 'EOF'
                    if inserter is not None:
                        readline.set_pre_input_hook(None)
                else:
                    print(self.prompt, file=self.stdout)
                    if line is not None:
                        os.write(self.stdin.fileno(), line.encode())
                    if not exec_now:
                        line = self.stdin.readline()
                    if len(line) == 0:
                        line = 'EOF'
                    else:
                        line = line.rstrip('\r\n')
                    if have_readline and line != 'EOF':
                        readline.add_history(line)
                self._load_remaining_input_into_queue()
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def cmdloop(self, intro=None):
        while not builtins.__tako_exit__:
            try:
                self._cmdloop(intro=intro)
            except KeyboardInterrupt:
                print()  # Gives a newline
                readline.set_pre_input_hook()
                fix_readline_state_after_ctrl_c()
                self.reset_buffer()
                intro = None

    @property
    def prompt(self):
        """Obtains the current prompt string."""
        global RL_LIB, RL_CAN_RESIZE
        if RL_CAN_RESIZE:
            # This is needed to support some system where line-wrapping doesn't
            # work. This is a bug in upstream Python, or possibly readline.
            RL_LIB.rl_reset_screen_size()
        return super().prompt
