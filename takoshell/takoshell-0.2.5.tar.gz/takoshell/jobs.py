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
"""Job control for the tako shell."""
import os
import sys
import time
import signal
import builtins
from collections import deque

from takoshell.platform import ON_DARWIN, ON_CYGWIN, ON_MSYS

tasks = deque()
# Track time stamp of last exit command, so that two consecutive attempts to
# exit can kill all jobs and exit.
_last_exit_time = None


if ON_DARWIN:
    def _send_signal(job, signal):
        # On OS X, os.killpg() may cause PermissionError when there are
        # any zombie processes in the process group.
        # See github issue #1012 for details
        for pid in job['pids']:
            if pid is None:  # the pid of an aliased proc is None
                continue
            os.kill(pid, signal)

elif ON_CYGWIN or ON_MSYS:
    # Similar to what happened on OSX, more issues on Cygwin
    # (see Github issue #514).
    def _send_signal(job, signal):
        try:
            os.killpg(job['pgrp'], signal)
        except Exception:
            for pid in job['pids']:
                try:
                    os.kill(pid, signal)
                except:
                    pass

else:
    def _send_signal(job, signal):
        try:
            os.killpg(job['pgrp'], signal)
        except Exception:
            for p in job['pids']:
                try:
                    os.kill(p, signal)
                except:
                    pass


def _continue(job):
    _send_signal(job, signal.SIGCONT)


def _kill(job):
    _send_signal(job, signal.SIGKILL)


def ignore_sigtstp():
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)


def _set_pgrp(info):
    pid = None
    for p in info['pids']:
        if p is not None:
            pid = p
            break
    if pid is None:
        # occurs if first process is an alias
        info['pgrp'] = None
        return
    try:
        info['pgrp'] = os.getpgid(pid)
    except ProcessLookupError:
        info['pgrp'] = None

_shell_pgrp = os.getpgrp()

_block_when_giving = (signal.SIGTTOU, signal.SIGTTIN,
                      signal.SIGTSTP, signal.SIGCHLD)

# _give_terminal_to is a simplified version of:
#    give_terminal_to from bash 4.3 source, jobs.c, line 4030
# this will give the terminal to the process group pgid
if ON_CYGWIN or ON_MSYS:
    import ctypes
    _libc = ctypes.CDLL('cygwin1.dll' if ON_CYGWIN else 'msys-2.0.dll')

    # on cygwin, signal.pthread_sigmask does not exist in Python, even
    # though pthread_sigmask is defined in the kernel.  thus, we use
    # ctypes to mimic the calls in the "normal" version below.
    def _give_terminal_to(pgid):
        if _shell_tty is not None and os.isatty(_shell_tty):
            omask = ctypes.c_ulong()
            mask = ctypes.c_ulong()
            _libc.sigemptyset(ctypes.byref(mask))
            for i in _block_when_giving:
                _libc.sigaddset(ctypes.byref(mask), ctypes.c_int(i))
            _libc.sigemptyset(ctypes.byref(omask))
            _libc.sigprocmask(ctypes.c_int(signal.SIG_BLOCK),
                              ctypes.byref(mask),
                              ctypes.byref(omask))
            _libc.tcsetpgrp(ctypes.c_int(_shell_tty), ctypes.c_int(pgid))
            _libc.sigprocmask(ctypes.c_int(signal.SIG_SETMASK),
                              ctypes.byref(omask), None)
else:
    def _give_terminal_to(pgid):
        if _shell_tty is not None and os.isatty(_shell_tty):
            oldmask = signal.pthread_sigmask(signal.SIG_BLOCK,
                                             _block_when_giving)
            os.tcsetpgrp(_shell_tty, pgid)
            signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)

# check for shell tty
try:
    _shell_tty = sys.stderr.fileno()
    if os.tcgetpgrp(_shell_tty) != os.getpgid(os.getpid()):
        # we don't own it
        _shell_tty = None
except OSError:
    _shell_tty = None


def wait_for_active_job():
    """
    Wait for the active job to finish, to be killed by SIGINT, or to be
    suspended by ctrl-z.
    """
    _clear_dead_jobs()

    active_task = get_next_task()

    # Return when there are no foreground active task
    if active_task is None:
        _give_terminal_to(_shell_pgrp)  # give terminal back to the shell
        return

    pgrp = active_task['pgrp']
    obj = active_task['obj']
    # give the terminal over to the fg process
    if pgrp is not None:
        _give_terminal_to(pgrp)

    _continue(active_task)

    _, wcode = os.waitpid(obj.pid, os.WUNTRACED)
    if os.WIFSTOPPED(wcode):
        print()  # get a newline because ^Z will have been printed
        active_task['status'] = "stopped"
    elif os.WIFSIGNALED(wcode):
        print()  # get a newline because ^C will have been printed
        obj.signal = (os.WTERMSIG(wcode), os.WCOREDUMP(wcode))
        obj.returncode = None
    else:
        obj.returncode = os.WEXITSTATUS(wcode)
        obj.signal = None

    return wait_for_active_job()


def get_next_task():
    """ Get the next active task and put it on top of the queue"""
    selected_task = None
    for tid in tasks:
        task = get_task(tid)
        if not task['bg'] and task['status'] == "running":
            selected_task = tid
            break
    if selected_task is None:
        return
    tasks.remove(selected_task)
    tasks.appendleft(selected_task)
    return get_task(selected_task)


def get_task(tid):
    return builtins.__tako_all_jobs__[tid]


def _clear_dead_jobs():
    to_remove = set()
    for tid in tasks:
        obj = get_task(tid)['obj']
        if obj.poll() is not None:
            to_remove.add(tid)
    for job in to_remove:
        tasks.remove(job)
        del builtins.__tako_all_jobs__[job]


def print_one_job(num, outfile=sys.stdout):
    """Print a line describing job number ``num``."""
    try:
        job = builtins.__tako_all_jobs__[num]
    except KeyError:
        return
    pos = '+' if tasks[0] == num else '-' if tasks[1] == num else ' '
    status = job['status']
    cmd = [' '.join(i) if isinstance(i, list) else i for i in job['cmds']]
    cmd = ' '.join(cmd)
    pid = job['pids'][-1]
    bg = ' &' if job['bg'] else ''
    print('[{}]{} {}: {}{} ({})'.format(num, pos, status, cmd, bg, pid),
          file=outfile)


def get_next_job_number():
    """Get the lowest available unique job number (for the next job created).
    """
    _clear_dead_jobs()
    i = 1
    while i in builtins.__tako_all_jobs__:
        i += 1
    return i

LAST_JOB_STARTED = None

def add_job(info):
    """
    Add a new job to the jobs dictionary.
    """
    global LAST_JOB_STARTED
    num = get_next_job_number()
    info['started'] = LAST_JOB_STARTED = time.time()
    info['status'] = "running"
    _set_pgrp(info)
    tasks.appendleft(num)
    builtins.__tako_all_jobs__[num] = info
    if info['bg']:
        print_one_job(num)


def clean_jobs():
    """Clean up jobs for exiting shell

    In non-interactive mode, kill all jobs.

    In interactive mode, check for suspended or background jobs, print a
    warning if any exist, and return False. Otherwise, return True.
    """
    jobs_clean = True
    if builtins.__tako_env__['TAKO_INTERACTIVE']:
        _clear_dead_jobs()

        if builtins.__tako_all_jobs__:
            global _last_exit_time

            if (_last_exit_time and LAST_JOB_STARTED and
                    _last_exit_time > LAST_JOB_STARTED):
                # Exit occurred after last command started, so it was called as
                # part of the last command and is now being called again
                # immediately. Kill jobs and exit without reminder about
                # unfinished jobs in this case.
                kill_all_jobs()
            else:
                if len(builtins.__tako_all_jobs__) > 1:
                    msg = 'there are unfinished jobs'
                else:
                    msg = 'there is an unfinished job'

                print()
                print('tako: {}'.format(msg), file=sys.stderr)
                print('-'*5, file=sys.stderr)
                jobs([], stdout=sys.stderr)
                print('-'*5, file=sys.stderr)
                print('Type "exit" or press "ctrl-d" again to force quit.',
                      file=sys.stderr)
                jobs_clean = False
                _last_exit_time = time.time()
    else:
        kill_all_jobs()

    return jobs_clean


def kill_all_jobs():
    """
    Send SIGKILL to all child processes (called when exiting tako).
    """
    _clear_dead_jobs()
    for job in builtins.__tako_all_jobs__.values():
        _kill(job)


def jobs(args, stdin=None, stdout=sys.stdout, stderr=None):
    """
    tako command: jobs

    Display a list of all current jobs.
    """
    _clear_dead_jobs()
    for j in tasks:
        print_one_job(j, outfile=stdout)
    return None, None


def disown(args, stdin=None):
    """
    tako command: disown

    Forget about a child process so it will keep running even if tako quits.
    If a single number is given as an argument, bring that job to the
    foreground. Additionally, specify "+" for the most recent job and "-" for
    the second most recent job.
    """

    _clear_dead_jobs()
    if len(tasks) == 0:
        return '', 'Cannot disown nonexistent job.\n'

    if len(args) == 0:
        act = tasks[0]  # take the last manipulated task by default
    elif len(args) == 1:
        try:
            if args[0] == '+':  # take the last manipulated task
                act = tasks[0]
            elif args[0] == '-':  # take the second to last manipulated task
                act = tasks[1]
            else:
                act = int(args[0])
        except (ValueError, IndexError):
            return '', 'Invalid job: {}\n'.format(args[0])

        if act not in builtins.__tako_all_jobs__:
            return '', 'Invalid job: {}\n'.format(args[0])
    else:
        return '', 'disown expects 0 or 1 arguments, not {}\n'.format(len(args))

    tasks.remove(act)
    del builtins.__tako_all_jobs__[act]


def fg(args, stdin=None):
    """
    tako command: fg

    Bring the currently active job to the foreground, or, if a single number is
    given as an argument, bring that job to the foreground. Additionally,
    specify "+" for the most recent job and "-" for the second most recent job.
    """

    _clear_dead_jobs()
    if len(tasks) == 0:
        return '', 'Cannot bring nonexistent job to foreground.\n'

    if len(args) == 0:
        act = tasks[0]  # take the last manipulated task by default
    elif len(args) == 1:
        try:
            if args[0] == '+':  # take the last manipulated task
                act = tasks[0]
            elif args[0] == '-':  # take the second to last manipulated task
                act = tasks[1]
            else:
                act = int(args[0])
        except (ValueError, IndexError):
            return '', 'Invalid job: {}\n'.format(args[0])

        if act not in builtins.__tako_all_jobs__:
            return '', 'Invalid job: {}\n'.format(args[0])
    else:
        return '', 'fg expects 0 or 1 arguments, not {}\n'.format(len(args))

    # Put this one on top of the queue
    tasks.remove(act)
    tasks.appendleft(act)

    job = get_task(act)
    job['bg'] = False
    job['status'] = "running"
    print_one_job(act)


def bg(args, stdin=None):
    """
    tako command: bg

    Resume execution of the currently active job in the background, or, if a
    single number is given as an argument, resume that job in the background.
    """
    res = fg(args, stdin)
    if res is None:
        curTask = get_task(tasks[0])
        curTask['bg'] = True
        _continue(curTask)
    else:
        return res
