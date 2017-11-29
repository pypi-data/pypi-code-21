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
"""Interface for running Python functions as subprocess-mode commands.

Code for several helper methods in the `ProcProxy` class have been reproduced
without modification from `subprocess.py` in the Python 3.4.2 standard library.
The contents of `subprocess.py` (and, thus, the reproduced methods) are
Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se> and were
licensed to the Python Software foundation under a Contributor Agreement.
"""
import io
import os
import sys
import signal
from functools import wraps
from threading import Thread
from collections import Sequence, namedtuple
from subprocess import PIPE, DEVNULL, STDOUT

from takoshell.tools import (redirect_stdout, redirect_stderr,
                         print_exception, TakoCalledProcessError)


class ProcProxy(Thread):
    """
    Class representing a function to be run as a subprocess-mode command.
    """
    def __init__(self, f, args,
                 stdin=None,
                 stdout=None,
                 stderr=None,
                 universal_newlines=False):
        """Parameters
        ----------
        f : function
            The function to be executed.
        args : list
            A (possibly empty) list containing the arguments that were given on
            the command line
        stdin : file-like, optional
            A file-like object representing stdin (input can be read from
            here).  If `stdin` is not provided or if it is explicitly set to
            `None`, then an instance of `io.StringIO` representing an empty
            file is used.
        stdout : file-like, optional
            A file-like object representing stdout (normal output can be
            written here).  If `stdout` is not provided or if it is explicitly
            set to `None`, then `sys.stdout` is used.
        stderr : file-like, optional
            A file-like object representing stderr (error output can be
            written here).  If `stderr` is not provided or if it is explicitly
            set to `None`, then `sys.stderr` is used.
        """
        self.f = f
        """
        The function to be executed.  It should be a function of four
        arguments, described below.

        Parameters
        ----------
        args : list
            A (possibly empty) list containing the arguments that were given on
            the command line
        stdin : file-like
            A file-like object representing stdin (input can be read from
            here).
        stdout : file-like
            A file-like object representing stdout (normal output can be
            written here).
        stderr : file-like
            A file-like object representing stderr (error output can be
            written here).
        """
        self.args = args
        self.pid = None
        self.returncode = None
        self.wait = self.join

        handles = self._get_handles(stdin, stdout, stderr)
        (self.p2cread, self.p2cwrite,
         self.c2pread, self.c2pwrite,
         self.errread, self.errwrite) = handles

        # default values
        self.stdin = stdin
        self.stdout = None
        self.stderr = None

        if self.p2cwrite != -1:
            self.stdin = io.open(self.p2cwrite, 'wb', -1)
            if universal_newlines:
                self.stdin = io.TextIOWrapper(self.stdin, write_through=True,
                                              line_buffering=False)
        if self.c2pread != -1:
            self.stdout = io.open(self.c2pread, 'rb', -1)
            if universal_newlines:
                self.stdout = io.TextIOWrapper(self.stdout)

        if self.errread != -1:
            self.stderr = io.open(self.errread, 'rb', -1)
            if universal_newlines:
                self.stderr = io.TextIOWrapper(self.stderr)

        Thread.__init__(self)
        self.start()

    def run(self):
        """Set up input/output streams and execute the child function in a new
        thread.  This is part of the `threading.Thread` interface and should
        not be called directly.
        """
        if self.f is None:
            return
        if self.stdin is not None:
            sp_stdin = io.TextIOWrapper(self.stdin)
        else:
            sp_stdin = io.StringIO("")

        if self.c2pwrite != -1:
            sp_stdout = io.TextIOWrapper(io.open(self.c2pwrite, 'wb', -1))
        else:
            sp_stdout = sys.stdout
        if self.errwrite == self.c2pwrite:
            sp_stderr = sp_stdout
        elif self.errwrite != -1:
            sp_stderr = io.TextIOWrapper(io.open(self.errwrite, 'wb', -1))
        else:
            sp_stderr = sys.stderr

        r = self.f(self.args, sp_stdin, sp_stdout, sp_stderr)
        self.returncode = 0 if r is None else r

    def poll(self):
        """Check if the function has completed.

        Returns
        -------
        `None` if the function is still executing, `True` if the function
        finished successfully, and `False` if there was an error.
        """
        return self.returncode

    # The code below (_get_devnull, and _get_handles) comes
    # from subprocess.py in the Python 3.4.2 Standard Library
    def _get_devnull(self):
        if not hasattr(self, '_devnull'):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        return self._devnull

    def _get_handles(self, stdin, stdout, stderr):
        """Construct and return tuple with IO objects:
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
        """
        p2cread, p2cwrite = -1, -1
        c2pread, c2pwrite = -1, -1
        errread, errwrite = -1, -1

        if stdin is None:
            pass
        elif stdin == PIPE:
            p2cread, p2cwrite = os.pipe()
        elif stdin == DEVNULL:
            p2cread = self._get_devnull()
        elif isinstance(stdin, int):
            p2cread = stdin
        else:
            # Assuming file-like object
            p2cread = stdin.fileno()

        if stdout is None:
            pass
        elif stdout == PIPE:
            c2pread, c2pwrite = os.pipe()
        elif stdout == DEVNULL:
            c2pwrite = self._get_devnull()
        elif isinstance(stdout, int):
            c2pwrite = stdout
        else:
            # Assuming file-like object
            c2pwrite = stdout.fileno()

        if stderr is None:
            pass
        elif stderr == PIPE:
            errread, errwrite = os.pipe()
        elif stderr == STDOUT:
            errwrite = c2pwrite
        elif stderr == DEVNULL:
            errwrite = self._get_devnull()
        elif isinstance(stderr, int):
            errwrite = stderr
        else:
            # Assuming file-like object
            errwrite = stderr.fileno()

        return (p2cread, p2cwrite,
                c2pread, c2pwrite,
                errread, errwrite)


def wrap_simple_command(f, args, stdin, stdout, stderr):
    """Decorator for creating 'simple' callable aliases."""
    bgable = getattr(f, '__tako_backgroundable__', True)
    @wraps(f)
    def wrapped_simple_command(args, stdin, stdout, stderr):
        try:
            i = stdin.read()
            if bgable:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    r = f(args, i)
            else:
                r = f(args, i)

            cmd_result = 0
            if isinstance(r, str):
                stdout.write(r)
            elif isinstance(r, Sequence):
                if r[0] is not None:
                    stdout.write(r[0])
                if r[1] is not None:
                    stderr.write(r[1])
                if len(r) > 2 and r[2] is not None:
                    cmd_result = r[2]
            elif r is not None:
                stdout.write(str(r))
            return cmd_result
        except Exception:
            print_exception()
            return 1  # returncode for failure
    return wrapped_simple_command


class SimpleProcProxy(ProcProxy):
    """Variant of `ProcProxy` for simpler functions.

    The function passed into the initializer for `SimpleProcProxy` should have
    the form described in the tako tutorial.  This function is then wrapped to
    make a new function of the form expected by `ProcProxy`.
    """

    def __init__(self, f, args, stdin=None, stdout=None, stderr=None,
                 universal_newlines=False):
        f = wrap_simple_command(f, args, stdin, stdout, stderr)
        super().__init__(f, args, stdin, stdout, stderr, universal_newlines)



def _wcode_to_popen(code):
    """Converts os.wait return code into Popen format."""
    if os.WIFEXITED(code):
        return os.WEXITSTATUS(code)
    elif os.WIFSIGNALED(code):
        return -1 * os.WTERMSIG(code)
    else:
        # Can this happen? Let's find out. Returning None is not an option.
        raise ValueError("Invalid os.wait code: {}".format(code))


_CCTuple = namedtuple("_CCTuple", ["stdin",
                                   "stdout",
                                   "stderr",
                                   "pid",
                                   "returncode",
                                   "args",
                                   "alias",
                                   "stdin_redirect",
                                   "stdout_redirect",
                                   "stderr_redirect",
                                   "timestamp",
                                   "executed_cmd"])


class CompletedCommand(_CCTuple):
    """Represents a completed subprocess-mode command."""

    def __bool__(self):
        return self.returncode == 0

    def __iter__(self):
        if not self.stdout:
            raise StopIteration()

        pre = self.stdout
        post = None

        while post != '':
            pre, sep, post = pre.partition('\n')
            # this line may be optional since we use universal newlines.
            pre = pre[:-1] if pre and pre[-1] == '\r' else pre
            yield pre
            pre = post


    def itercheck(self):
        yield from self
        if self.returncode:
            # I included self, as providing access to stderr and other details
            # useful when instance isn't assigned to a variable in the shell.
            raise TakoCalledProcessError(self.returncode, self.executed_cmd,
                                          self.stdout, self.stderr, self)

    @property
    def inp(self):
        """Creates normalized input string from args."""
        return ' '.join(self.args)

    @property
    def out(self):
        """Alias to stdout."""
        return self.stdout

    @property
    def err(self):
        """Alias to stderr."""
        return self.stderr

    @property
    def rtn(self):
        """Alias to return code."""
        return self.returncode

CompletedCommand.__new__.__defaults__ = (None,) * len(CompletedCommand._fields)


class HiddenCompletedCommand(CompletedCommand):
    def __repr__(self):
        return ''


def pause_call_resume(p, f, *args, **kwargs):
    """For a process p, this will call a function f with the remaining args and
    and kwargs. If the process cannot accept signals, the function will be called.

    Parameters
    ----------
    p : Popen object or similar
    f : callable
    args : remaining arguments
    kwargs : keyword arguments
    """
    can_send_signal = hasattr(p, 'send_signal')
    if can_send_signal:
        p.send_signal(signal.SIGSTOP)
    try:
        f(*args, **kwargs)
    except Exception:
        pass
    if can_send_signal:
        p.send_signal(signal.SIGCONT)
