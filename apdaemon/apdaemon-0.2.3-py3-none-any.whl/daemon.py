# -*- coding:utf-8 -*-

import os
import sys
import atexit
import signal
from functools import wraps, partial

import psutil

__all__ = [
    "daemon"
]

LOGGER_WARNING = "\033[41;33m\033[1m\033[4mWARNING\033[0m"
LOGGER_INFO = "\033[40;32m\033[1m\033[4mINFO\033[0m"
LOGGER_ERROR = "\033[40;31m\033[1m\033[4mERROR\033[0m"

PROCESS_STOPPED = "STOPPED"
PROCESS_RUNNING = "RUNNING"


def __logger(service, pidfile, stdin, stdout, stderr, work_dir, pid,
             level=LOGGER_INFO, status=PROCESS_RUNNING):

    template = ("{level} {service} is \033[40;35m{status}\033[0m, pid is {pid}\n"
                "|_______ pidfile  located  at: {pidfile}\n"
                "|_______ stdin    from     at: {stdin}\n"
                "|_______ stdout   redirect to: {stdout}\n"
                "|_______ stderr   redirect to: {stderr}\n"
                "|_______ work_dir located  at: {work_dir}\n")

    msg = template.format(**locals())

    print(msg, file=sys.stdout)


def __check_process_is_running(pid):
    try:
        return psutil.Process(int(pid)).status() == psutil._common.STATUS_RUNNING
    except (psutil.NoSuchProcess, ValueError, Exception):
        return False


def daemon(service, pidfile="/tmp/python-daemon.pid",
           stdin="/dev/null", stdout="/tmp/python-daemon.log", stderr="/tmp/python-daemon.log",
           work_dir="/"):
    """
    ----------------------------------------------
            run process in daemon way.
    ----------------------------------------------

    >>> from apdaemon.daemon import daemon
    >>> @daemon(service="maind")
    >>> def main():
    >>>     import time
    >>>     while True:
    >>>           print("hello world")
    >>>           time.sleep(3)
    >>> main()

    * service:  service name;
    * pidfile:  daemon process pid file;
    * stdin:    stdin;
    * stdout:   stdout redirect;
    * stderr:   stderr redirect.
    * work_dir: daemon process work directory.
    """
    printf = partial(__logger, service, pidfile, stdin, stdout, stderr, work_dir)

    def start():

        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                printf(pid, LOGGER_ERROR, PROCESS_RUNNING)
                sys.exit(0)
            else:
                os.remove(pidfile)

        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError:
            raise RuntimeError("fork #1 failed.")

        os.chdir(work_dir)
        os.umask(0)
        os.setsid()

        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError:
            raise RuntimeError("fork #2 failed.")

        sys.stdout.flush()
        sys.stderr.flush()

        with open(stdin, "rb", 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(stdout, "ab", 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(stderr, "ab", 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))

        def remove_pidfile_atexit():
            if os.path.exists(pidfile):
                os.remove(pidfile)

        atexit.register(remove_pidfile_atexit)

        def term_signal_handler(sig, frame):
            remove_pidfile_atexit()
            raise SystemExit(1)

        signal.signal(signal.SIGTERM, term_signal_handler)

    def stop(exit_=True):
        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                os.kill(int(pid), signal.SIGTERM)
            os.remove(pidfile)

        if exit_ is True:
            sys.exit(0)

    def status():
        running = False
        pid = ""
        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                running = True

        if running is False:
            printf(pid, LOGGER_WARNING, PROCESS_STOPPED)
        else:
            printf(pid, LOGGER_INFO, PROCESS_RUNNING)
        sys.exit(0)

    def restart():
        stop(exit_=False)
        start()

    command = sys.argv[1] if len(sys.argv) >= 2 else "start"
    if command in ["start", "stop", "restart", "status"]:
        locals()[command]()
    else:
        print("UNSUPPORTED COMMAND!")
        sys.exit(0)

    def decorate(func):
        @wraps(func)
        def execute(*args, **kwargs):
            return func(*args, **kwargs)
        return execute
    return decorate
