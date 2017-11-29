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
"""The tako built-ins.

Note that this module is named 'built_ins' so as not to be confused with the
special Python builtins module.
"""
import os
import re
import ast
import sys
import time
import shlex
import signal
import inspect
import builtins
import tempfile

from fractions import Fraction
from collections import Sequence
from contextlib import contextmanager
from subprocess import Popen, PIPE, STDOUT, CalledProcessError

from takoshell.events import fire_event
from takoshell.braceexpand import braceexpand
from takoshell.environ import Env, default_env, locate_binary
from takoshell.jobs import add_job, wait_for_active_job
from takoshell.proc import (ProcProxy, SimpleProcProxy,
                        CompletedCommand, HiddenCompletedCommand)

import takoshell.tools
from takoshell.tools import TakoError, TakoCalledProcessError

BUILTINS_LOADED = False
AT_EXIT_SIGNALS = (signal.SIGABRT, signal.SIGFPE, signal.SIGILL, signal.SIGSEGV,
                   signal.SIGTERM, signal.SIGTSTP, signal.SIGQUIT, signal.SIGHUP)

SIGNAL_MESSAGES = {
    signal.SIGABRT: 'Aborted',
    signal.SIGFPE: 'Floating point exception',
    signal.SIGILL: 'Illegal instructions',
    signal.SIGTERM: 'Terminated',
    signal.SIGSEGV: 'Segmentation fault',
    signal.SIGQUIT: 'Quit',
    signal.SIGHUP: 'Hangup',
    signal.SIGKILL: 'Killed'
}

def resetting_signal_handle(sig, f):
    """Sets a new signal handle that will automatically restore the old value
    once the new handle is finished.
    """
    oldh = signal.getsignal(sig)

    def newh(s=None, frame=None):
        f(s, frame)
        signal.signal(sig, oldh)
        if sig != 0:
            sys.exit(sig)
    signal.signal(sig, newh)


def expand_path(s):
    """Takes a string path and expands ~ to home and environment vars."""
    if builtins.__tako_env__['TAKO_SETTINGS'].expand_env_vars:
        s = takoshell.tools.expandvars(s)
    return os.path.expanduser(s)


def reglob(path, parts=None, i=None):
    """Regular expression-based globbing."""
    if parts is None:
        path = os.path.normpath(path)
        drive, tail = os.path.splitdrive(path)
        parts = tail.split(os.sep)
        d = os.sep if os.path.isabs(path) else '.'
        d = os.path.join(drive, d)
        return reglob(d, parts, i=0)
    base = subdir = path
    if i == 0:
        if not os.path.isabs(base):
            base = ''
        elif len(parts) > 1:
            i += 1
    regex = os.path.join(base, parts[i])
    regex = re.compile(regex)
    files = os.listdir(subdir)
    files.sort()
    paths = []
    i1 = i + 1
    if i1 == len(parts):
        for f in files:
            p = os.path.join(base, f)
            if regex.fullmatch(p) is not None:
                paths.append(p)
    else:
        for f in files:
            p = os.path.join(base, f)
            if regex.fullmatch(p) is None or not os.path.isdir(p):
                continue
            paths += reglob(p, parts=parts, i=i1)
    return paths


def regexsearch(s):
    s = expand_path(s)
    return reglob(s)


def globsearch(s):
    env = builtins.__tako_env__
    csc = env['TAKO_SETTINGS'].CASE_SENSITIVE_COMPLETIONS
    test_strings = braceexpand(s)
    return sum((list(takoshell.tools.globpath(s, ignore_case=(not csc), return_empty=True))
                for s in test_strings), [])


def pathsearch(func, s, pymode=False):
    """
    Takes a string and returns a list of file paths that match (regex, glob,
    or arbitrary search function).
    """
    if (not callable(func) or
            len(inspect.signature(func).parameters) != 1):
        error = "%r is not a known path search function"
        raise TakoError(error % func)
    o = func(s)
    no_match = [] if pymode else [s]
    return o if len(o) != 0 else no_match

RE_SHEBANG = re.compile(r'#![ \t]*(.+?)$')


def _is_binary(fname, limit=80):
    with open(fname, 'rb') as f:
        for i in range(limit):
            char = f.read(1)
            if char == b'\0':
                return True
            if char == b'\n':
                return False
            if char == b'':
                return False
    return False


def _frac_repr(_self):
    return '%s/%s' % (_self.numerator, _self.denominator)

Fraction.__repr__ = Fraction.__str__ = _frac_repr


def tako_num(x):
    nmode = builtins.__tako_env__['TAKO_SETTINGS'].number_mode
    if nmode in {'python', 'hybrid'}:
        try:
            return ast.literal_eval(x)
        except:
            return ast.literal_eval(x.replace('_', ''))
    elif nmode == 'exact':
        try:
            return int(x)
        except:
            try:
                return Fraction(x)
            except:
                return ast.literal_eval(x)
    else:
        raise TakoError('Invalid number mode: %s' % nmode)

def make_tako_op(opdict):
    def _tako_op(x, y):
        nmode = builtins.__tako_env__['TAKO_SETTINGS'].number_mode
        if nmode in opdict:
            return opdict[nmode](x, y)
        else:
            raise TakoError('Invalid number mode: %s' % nmode)
    return _tako_op

def _exact_div(x, y):
    if any(isinstance(i, (float, complex)) for i in (x, y)):
        return x / y
    else:
        n = Fraction(x, y)
        if n.denominator == 1:
            return n.numerator
        return n

def _exact_floordiv(x, y):
    if any(isinstance(i, (float, complex)) for i in (x, y)):
        return x // y
    else:
        return Fraction(x, y).__floor__()

tako_div = make_tako_op({'python': lambda x,y: x / y,
                         'exact': _exact_div,
                         'hybrid': _exact_div})

tako_floordiv = make_tako_op({'python': lambda x,y: x // y,
                              'exact': _exact_floordiv,
                              'hybrid': _exact_floordiv})


def get_script_subproc_command(fname, args):
    """
    Given the name of a script outside the path, returns a list representing
    an appropriate subprocess command to execute the script.  Raises
    PermissionError if the script is not executable.
    """
    # make sure file is executable
    if not os.access(fname, os.X_OK):
        raise PermissionError

    if not os.access(fname, os.R_OK):
        # on some systems, some important programs (e.g. sudo) will have
        # execute permissions but not read/write permisions. This enables
        # things with the SUID set to be run. Needs to come before _is_binary()
        # is called, because that function tries to read the file.
        return [fname] + args
    elif _is_binary(fname):
        # if the file is a binary, we should call it directly
        return [fname] + args

    # find interpreter
    with open(fname, 'rb') as f:
        first_line = f.readline().decode().strip()
    m = RE_SHEBANG.match(first_line)

    # tako is the default interpreter
    if m is None:
        interp = ['tako']
    else:
        interp = m.group(1).strip()
        if len(interp) > 0:
            interp = shlex.split(interp)
        else:
            interp = ['tako']

    return interp + [fname] + args


_REDIR_NAME = "(o(?:ut)?|e(?:rr)?|a(?:ll)?|&?\d?)"
_REDIR_REGEX = re.compile("{r}(>?>|<){r}$".format(r=_REDIR_NAME))
_MODES = {'>>': 'a', '>': 'w', '<': 'r'}
_WRITE_MODES = frozenset({'w', 'a'})
_REDIR_ALL = frozenset({'&', 'a', 'all'})
_REDIR_ERR = frozenset({'2', 'e', 'err'})
_REDIR_OUT = frozenset({'', '1', 'o', 'out'})
_E2O_MAP = frozenset({'{}>{}'.format(e, o)
                      for e in _REDIR_ERR
                      for o in _REDIR_OUT
                      if o != ''})


def _is_redirect(x):
    return isinstance(x, str) and _REDIR_REGEX.match(x)


def _open(fname, mode):
    # file descriptors
    if isinstance(fname, int):
        return fname
    try:
        return open(fname, mode)
    except PermissionError:
        raise TakoError('tako: {0}: permission denied'.format(fname))
    except FileNotFoundError:
        raise TakoError('tako: {0}: no such file or directory'.format(fname))
    except Exception:
        raise TakoError('tako: {0}: unable to open file'.format(fname))


def _redirect_io(streams, r, loc=None):
    # special case of redirecting stderr to stdout
    if r.replace('&', '') in _E2O_MAP:
        if 'stderr' in streams:
            raise TakoError('Multiple redirects for stderr')
        streams['stderr'] = ('<stdout>', 'a', STDOUT)
        return

    orig, mode, dest = _REDIR_REGEX.match(r).groups()

    # redirect to fd
    if dest.startswith('&'):
        try:
            dest = int(dest[1:])
            if loc is None:
                loc, dest = dest, ''
            else:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise TakoError(e)
        except (ValueError, TakoError):
            raise
        except Exception:
            pass

    mode = _MODES.get(mode, None)

    if mode == 'r':
        if len(orig) > 0 or len(dest) > 0:
            raise TakoError('Unrecognized redirection command: {}'.format(r))
        elif 'stdin' in streams:
            raise TakoError('Multiple inputs for stdin')
        else:
            streams['stdin'] = (loc, 'r', _open(loc, mode))
    elif mode in _WRITE_MODES:
        if orig in _REDIR_ALL:
            if 'stderr' in streams:
                raise TakoError('Multiple redirects for stderr')
            elif 'stdout' in streams:
                raise TakoError('Multiple redirects for stdout')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise TakoError(e)
            targets = ['stdout', 'stderr']
        elif orig in _REDIR_ERR:
            if 'stderr' in streams:
                raise TakoError('Multiple redirects for stderr')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise TakoError(e)
            targets = ['stderr']
        elif orig in _REDIR_OUT:
            if 'stdout' in streams:
                raise TakoError('Multiple redirects for stdout')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise TakoError(e)
            targets = ['stdout']
        else:
            raise TakoError('Unrecognized redirection command: {}'.format(r))

        f = _open(loc, mode)
        for t in targets:
            streams[t] = (loc, mode, f)

    else:
        raise TakoError('Unrecognized redirection command: {}'.format(r))


def run_subproc(cmds, captured=False):
    """Runs a subprocess, in its many forms. This takes a list of 'commands,'
    which may be a list of command line arguments or a string, representing
    a special connecting character.  For example::

        $ ls | grep wakka

    is represented by the following cmds::

        [['ls'], '|', ['grep', 'wakka']]

    Lastly, the captured argument affects only the last real command.
    """
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    aliases = settings.aliases
    background = False
    procinfo = {}
    if cmds[-1] == '&':
        background = True
        cmds = cmds[:-1]
    _pipeline_group = None
    write_target = None
    last_cmd = len(cmds) - 1
    procs = []
    prev_proc = None
    _capture_streams = captured in {'stdout', 'object'}
    for ix, cmd in enumerate(cmds):
        ocmd = cmd
        starttime = time.time()
        procinfo['args'] = list(cmd)
        stdin = None
        stderr = None
        if isinstance(cmd, str):
            continue
        streams = {}
        while True:
            if len(cmd) >= 3 and _is_redirect(cmd[-2]):
                _redirect_io(streams, cmd[-2], cmd[-1])
                cmd = cmd[:-2]
            elif len(cmd) >= 2 and _is_redirect(cmd[-1]):
                _redirect_io(streams, cmd[-1])
                cmd = cmd[:-1]
            elif len(cmd) >= 3 and cmd[0] == '<':
                _redirect_io(streams, cmd[0], cmd[1])
                cmd = cmd[2:]
            else:
                break
        # set standard input
        if 'stdin' in streams:
            if prev_proc is not None:
                raise TakoError('Multiple inputs for stdin')
            stdin = streams['stdin'][-1]
            procinfo['stdin_redirect'] = streams['stdin'][:-1]
        elif prev_proc is not None:
            stdin = prev_proc.stdout
        # set standard output
        _stdout_name = None
        _stderr_name = None
        if 'stdout' in streams:
            if ix != last_cmd:
                raise TakoError('Multiple redirects for stdout')
            stdout = streams['stdout'][-1]
            procinfo['stdout_redirect'] = streams['stdout'][:-1]
        elif ix != last_cmd:
            stdout = PIPE
        elif _capture_streams:
            _nstdout = stdout = tempfile.NamedTemporaryFile(delete=False)
            _stdout_name = stdout.name
        elif builtins.__tako_stdout_uncaptured__ is not None:
            stdout = builtins.__tako_stdout_uncaptured__
        else:
            stdout = None
        # set standard error
        if 'stderr' in streams:
            stderr = streams['stderr'][-1]
            procinfo['stderr_redirect'] = streams['stderr'][:-1]
        elif captured == 'object' and ix == last_cmd:
            _nstderr = stderr = tempfile.NamedTemporaryFile(delete=False)
            _stderr_name = stderr.name
        elif builtins.__tako_stderr_uncaptured__ is not None:
            stderr = builtins.__tako_stderr_uncaptured__
        uninew = (ix == last_cmd) and (not _capture_streams)

        if callable(cmd[0]):
            alias = cmd[0]
        else:
            alias = aliases.get(cmd[0], None)

        if alias is None:  # look in plugins for the alias
            for plugin in settings.plugins:
                alias = settings.plugins[plugin].aliases.get(cmd[0], None)
                if alias is not None:
                    break

        procinfo['alias'] = alias
        if alias is None:
            binary_loc = locate_binary(cmd[0])
        elif not callable(alias):
            binary_loc = locate_binary(alias[0])
        if (alias is None and
                settings.auto_cd and
                len(cmd) == 1 and
                os.path.isdir(cmd[0]) and
                binary_loc is None):
            cmd.insert(0, 'cd')
            alias = aliases.get('cd', None)

        if callable(alias):
            aliased_cmd = alias
        else:
            if alias is not None:
                aliased_cmd = alias + cmd[1:]
            else:
                aliased_cmd = cmd
            if binary_loc is not None:
                try:
                    aliased_cmd = get_script_subproc_command(binary_loc,
                                                             aliased_cmd[1:])
                except PermissionError:
                    e = 'tako: subprocess mode: permission denied: {0}'
                    raise TakoError(e.format(cmd[0]))
        _stdin_file = None
        if (stdin is not None and
                settings.store_stdin and
                captured == 'object' and
                'cat' in builtins.__tako_commands_cache__ and
                'tee' in builtins.__tako_commands_cache__):
            _stdin_file = tempfile.NamedTemporaryFile()
            cproc = Popen(['cat'],
                          stdin=stdin,
                          stdout=PIPE)
            tproc = Popen(['tee', _stdin_file.name],
                          stdin=cproc.stdout,
                          stdout=PIPE)
            stdin = tproc.stdout
        if callable(aliased_cmd):
            prev_is_proxy = True
            numargs = len(inspect.signature(aliased_cmd).parameters)
            if numargs == 2:
                cls = SimpleProcProxy
            elif numargs == 4:
                cls = ProcProxy
            else:
                e = 'Expected callable with 2 or 4 arguments, not {}'
                raise TakoError(e.format(numargs))
            proc = cls(aliased_cmd, cmd[1:],
                       stdin, stdout, stderr,
                       universal_newlines=uninew)
        else:
            prev_is_proxy = False
            cls = Popen
            subproc_kwargs = {}
            if cls is Popen:
                def _subproc_pre():
                    if _pipeline_group is None:
                        os.setpgrp()
                    else:
                        os.setpgid(0, _pipeline_group)
                    signal.signal(signal.SIGTSTP, lambda n, f: signal.pause())
                subproc_kwargs['preexec_fn'] = _subproc_pre
            denv = env.detype()
            try:
                proc = cls([str(i) for i in aliased_cmd],
                           universal_newlines=uninew,
                           env=denv,
                           stdin=stdin,
                           stdout=stdout,
                           stderr=stderr,
                           **subproc_kwargs)
            except PermissionError:
                e = 'tako: subprocess mode: permission denied: {0}'
                raise TakoError(e.format(aliased_cmd[0]))
            except FileNotFoundError:
                cmd = aliased_cmd[0]
                e = 'tako: subprocess mode: command not found: {0}'.format(cmd)
                sug = takoshell.tools.suggest_commands(cmd, env, aliases) or ''
                if len(sug.strip()) > 0:
                    e += '\n' + sug
                raise TakoError(e)
        fire_event('pre_command', ocmd)
        procs.append(proc)
        prev_proc = proc
        if cls is Popen and _pipeline_group is None:
            _pipeline_group = prev_proc.pid
    if not prev_is_proxy:
        add_job({
            'cmds': cmds,
            'pids': [i.pid for i in procs],
            'obj': prev_proc,
            'bg': background,
        })
    if (env.get('TAKO_INTERACTIVE') and
            not _capture_streams):
        # set title here to get current command running
        builtins.__tako_shell__.settitle()
    if background:
        return
    if prev_is_proxy:
        prev_proc.wait()
    wait_for_active_job()
    for proc in procs[:-1]:
        try:
            proc.stdout.close()
        except OSError:
            pass
    # get output
    output = b''
    if write_target is None:
        if _stdout_name is not None:
            with open(_stdout_name, 'rb') as stdoutfile:
                output = stdoutfile.read()
            try:
                _nstdout.close()
            except:
                pass
            os.unlink(_stdout_name)
        elif prev_proc.stdout not in (None, sys.stdout):
            output = prev_proc.stdout.read()
        if _capture_streams:
            # to get proper encoding from Popen, we have to
            # use a byte stream and then implement universal_newlines here
            output = output.decode(encoding=settings.encoding)
            output = output.replace('\r\n', '\n').rstrip('\n')
        if captured == 'object': # get stderr as well
            named = _stderr_name is not None
            unnamed = prev_proc.stderr not in {None, sys.stderr}
            if named:
                with open(_stderr_name, 'rb') as stderrfile:
                    errout = stderrfile.read()
                try:
                    _nstderr.close()
                except:
                    pass
                os.unlink(_stderr_name)
            elif unnamed:
                errout = prev_proc.stderr.read()
            if named or unnamed:
                errout = errout.decode(encoding=settings.encoding,
                                       errors=settings.encoding_errors)
                errout = errout.replace('\r\n', '\n')
                procinfo['stderr'] = errout

    if getattr(prev_proc, 'signal', None):
        sig, core = prev_proc.signal
        sig_str = SIGNAL_MESSAGES.get(sig)
        if sig_str:
            if core:
                sig_str += ' (core dumped)'
            print(sig_str, file=sys.stderr)
    if (not prev_is_proxy and
            settings.raise_subproc_error):
        raise CalledProcessError(prev_proc.returncode, aliased_cmd, output=output)
    if captured == 'stdout':
        fire_event('post_command', output)
        return output
    elif captured is not False:
        procinfo['executed_cmd'] = aliased_cmd
        procinfo['pid'] = prev_proc.pid
        procinfo['returncode'] = prev_proc.returncode
        procinfo['timestamp'] = (starttime, time.time())
        if captured == 'object':
            procinfo['stdout'] = output
            if _stdin_file is not None:
                _stdin_file.seek(0)
                procinfo['stdin'] = _stdin_file.read().decode()
                _stdin_file.close()
            out = CompletedCommand(**procinfo)
            fire_event('post_command', out)
            return out
        else:
            out = HiddenCompletedCommand(**procinfo)
            fire_event('post_command', out)
            return out


def subproc_captured_stdout(*cmds):
    """Runs a subprocess, capturing the output. Returns the stdout
    that was produced as a str.
    """
    return run_subproc(cmds, captured='stdout')


def subproc_captured_inject(*cmds):
    """Runs a subprocess, capturing the output. Returns a list of
    whitespace-separated strings in the stdout that was produced."""
    return [i.strip() for i in run_subproc(cmds, captured='stdout').strip().split()]


def subproc_captured_object(*cmds):
    """
    Runs a subprocess, capturing the output. Returns an instance of
    ``CompletedCommand`` representing the completed command.
    """
    return run_subproc(cmds, captured='object')


def subproc_captured_hiddenobject(*cmds):
    """
    Runs a subprocess, capturing the output. Returns an instance of
    ``HiddenCompletedCommand`` representing the completed command.
    """
    return run_subproc(cmds, captured='hiddenobject')


def subproc_uncaptured(*cmds):
    """Runs a subprocess, without capturing the output. Returns the stdout
    that was produced as a str.
    """
    return run_subproc(cmds, captured=False)


def ensure_list_of_strs(x):
    """Ensures that x is a list of strings."""
    if isinstance(x, str):
        rtn = [x]
    elif isinstance(x, Sequence):
        rtn = [i if isinstance(i, str) else str(i) for i in x]
    else:
        rtn = [str(x)]
    return rtn


def list_of_strs_or_callables(x):
    """Ensures that x is a list of strings or functions"""
    if isinstance(x, str) or callable(x):
        rtn = [x]
    else:
        try:
            rtn = [i if isinstance(i, str) or callable(i) else str(i) for i in x]
        except TypeError:
            rtn = [str(x)]
    return rtn


def load_builtins(execer=None, login=False, ctx=None):
    """Loads the tako builtins into the Python builtins. Sets the
    BUILTINS_LOADED variable to True.
    """
    global BUILTINS_LOADED, env
    # private built-ins
    builtins.__tako_config__ = {}
    builtins.__tako_env__ = env = Env(default_env(login=login))
    builtins.__tako_pathsearch__ = pathsearch
    builtins.__tako_globsearch__ = globsearch
    builtins.__tako_regexsearch__ = regexsearch
    builtins.__tako_glob__ = takoshell.tools.globpath
    builtins.__tako_expand_path__ = expand_path
    builtins.__tako_exit__ = False
    builtins.__tako_stdout_uncaptured__ = None
    builtins.__tako_stderr_uncaptured__ = None
    if hasattr(builtins, 'exit'):
        builtins.__tako_pyexit__ = builtins.exit
        del builtins.exit
    if hasattr(builtins, 'quit'):
        builtins.__tako_pyquit__ = builtins.quit
        del builtins.quit
    builtins.__tako_subproc_captured_stdout__ = subproc_captured_stdout
    builtins.__tako_subproc_captured_inject__ = subproc_captured_inject
    builtins.__tako_subproc_captured_object__ = subproc_captured_object
    builtins.__tako_subproc_captured_hiddenobject__ = subproc_captured_hiddenobject
    builtins.__tako_subproc_uncaptured__ = subproc_uncaptured
    builtins.__tako_execer__ = execer
    builtins.__tako_commands_cache__ = takoshell.tools.CommandsCache()
    builtins.__tako_all_jobs__ = {}
    builtins.__tako_ensure_list_of_strs__ = ensure_list_of_strs
    builtins.__tako_list_of_strs_or_callables__ = list_of_strs_or_callables
    builtins.__tako_num__ = tako_num
    builtins.__tako_div__ = tako_div
    builtins.__tako_floordiv__ = tako_floordiv
    # public built-ins
    builtins.TakoError = TakoError
    builtins.TakoCalledProcessError = TakoCalledProcessError
    builtins.evalx = None if execer is None else execer.eval
    builtins.execx = None if execer is None else execer.exec
    builtins.compilex = None if execer is None else execer.compile
    BUILTINS_LOADED = True


def unload_builtins():
    """Removes the tako builtins from the Python builtins, if the
    BUILTINS_LOADED is True, sets BUILTINS_LOADED to False, and returns.
    """
    global BUILTINS_LOADED
    env = getattr(builtins, '__tako_env__', None)
    if isinstance(env, Env):
        env.undo_replace_env()
    if hasattr(builtins, '__tako_pyexit__'):
        builtins.exit = builtins.__tako_pyexit__
    if hasattr(builtins, '__tako_pyquit__'):
        builtins.quit = builtins.__tako_pyquit__
    if not BUILTINS_LOADED:
        return
    names = ['__tako_config__',
             '__tako_env__',
             '__tako_ctx__',
             '__tako_pathsearch__',
             '__tako_globsearch__',
             '__tako_regexsearch__',
             '__tako_glob__',
             '__tako_expand_path__',
             '__tako_exit__',
             '__tako_stdout_uncaptured__',
             '__tako_stderr_uncaptured__',
             '__tako_pyexit__',
             '__tako_pyquit__',
             '__tako_subproc_captured_stdout__',
             '__tako_subproc_captured_inject__',
             '__tako_subproc_captured_object__',
             '__tako_subproc_captured_hiddenobject__',
             '__tako_subproc_uncaptured__',
             '__tako_execer__',
             '__tako_commands_cache__',
             '__tako_num__',
             '__tako_div__',
             '__tako_floordiv__',
             'TakoError',
             'TakoCalledProcessError',
             'evalx',
             'execx',
             'compilex',
             '__tako_all_jobs__',
             '__tako_ensure_list_of_strs__',
             '__tako_list_of_strs_or_callables__',
             ]
    for name in names:
        if hasattr(builtins, name):
            delattr(builtins, name)
    BUILTINS_LOADED = False


@contextmanager
def tako_builtins(execer=None):
    """A context manager for using the tako builtins only in a limited
    scope. Likely useful in testing.
    """
    load_builtins(execer=execer)
    yield
    unload_builtins()
