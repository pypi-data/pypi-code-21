# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import errno
import logging
import logging.handlers
import os
from pkg_resources import resource_filename
import signal
import time
import sys

from appdynamics.scripts.pyagent import CommandInvocationError, CommandExecutionError, parse_options
from appdynamics.lang import bytes, str
from appdynamics.lib import default_log_formatter
from appdynamics import config

USAGE = "proxy <command> [args...]"
ABOUT = """Manage the AppDynamics proxy service

MANUALLY STARTING THE PROXY
    To manually start the proxy:

        {pyagent} proxy start [--debug] [--no-watchdog] [args...]

    By default, the proxy will be started with a watchdog process that
    restarts the proxy if it dies for any reason.

    Any additional arguments passed after the node name are passed to the
    proxy.

        --debug             start the proxy in debugging mode
        --no-watchdog       disable the proxy watchdog (not recommended)

MANUALLY STOPPING THE PROXY
    To stop a proxy started by the {pyagent} script:

        {pyagent} proxy stop

    If the watchdog is running, this will stop the watchdog before stopping
    the proxy.

RESTARTING THE PROXY
    To restart a proxy started by the {pyagent} script:

        {pyagent} proxy restart

    This is equivalent to stopping and then starting the proxy. This command
    works even if the proxy is not currently running (but does not work if
    the proxy was started by something other than the {pyagent} script)."""


MAX_WATCHDOG_LOG_BYTES = 10 * 10**6
PROXY_START_TIMEOUT = 0.5


def command(options, args):
    if not args:
        raise CommandInvocationError('missing required proxy command')

    SUBCOMMANDS = {'start': start, 'stop': stop, 'restart': restart}
    subcommand = args[0]

    if subcommand not in SUBCOMMANDS:
        raise CommandInvocationError('unrecognized proxy command: %s' % subcommand)

    SUBCOMMANDS[subcommand](args[1:])


START_OPTIONS = {
    'debug': {
        'short': 'd',
        'help': 'start proxy in debug mode',
    },
    'no-watchdog': 'disable the watchdog that ensures the proxy remains running',

    'run-proxy-script': {   # Internal/undocumented
        'short': 's',
        'help': False,      # Specify the name of the run proxy script (normally auto-discovered)
        'value': True,
    },
    'config-file': {
        'short': 'c',
        'help': 'the config file to use',
        'value': True,
        'value_help': '<file>',
    },
}


def process_config(options):
    if 'config-file' in options:
        os.environ['APPD_CONFIG_FILE'] = options['config-file']
    proxy_config = config.parse_environ()
    config.merge(proxy_config)


def get_watchdog_pid_file():
    return os.path.join(config.PROXY_RUN_DIR, 'watchdog.pid')


def get_proxy_pid_file():
    return os.path.join(config.PROXY_RUN_DIR, 'proxy.pid')


def start(args=None):
    options, args = parse_options(START_OPTIONS, args or [])

    process_config(options)
    create_dirs()

    run_proxy_script = options.get('run-proxy-script', None)
    use_watchdog = 'no-watchdog' not in options
    debug = 'debug' in options
    logger = configure_proxy_logger(debug)

    start_fn = start_watchdog if use_watchdog else start_proxy
    proxy_pid = start_fn(run_proxy_script=run_proxy_script, script_args=args, debug=debug)

    if not use_watchdog:
        logger.info('started proxy with pid %d' % proxy_pid)


def stop(args=None):
    options, args = parse_options(START_OPTIONS, args or [])
    process_config(options)
    watchdog_pid_file = get_watchdog_pid_file()
    if os.path.exists(watchdog_pid_file):
        try:
            stop_process('watchdog', watchdog_pid_file)
        except:
            pass  # It's ok if the watchdog isn't running.

    return stop_process('proxy', get_proxy_pid_file())


def restart(args=None):
    try:
        pid = stop(args)
        while is_process_alive(pid):
            # wait for the proxy to stop
            pass
    except CommandExecutionError:
        # proxy wasn't running
        pass

    start(args)


def create_dirs():
    def mkdir(path, mode=0o777):
        try:
            os.makedirs(path, mode)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    mkdir(config.PROXY_RUN_DIR)
    mkdir(config.PROXY_CONTROL_PATH)
    mkdir(config.LOGS_DIR)


def is_process_alive(pid):
    try:
        os.kill(pid, 0)  # "Are you there?" (see `man 2 kill`)
    except OSError as exc:
        # Can only get permission denied if there's a process we can't send signals to.
        # Other errors indicate that process with given pid doesn't exist.
        return exc.errno == errno.EPERM

    return True  # Process exists.


def unlink(filename):
    try:
        os.unlink(filename)
    except:
        pass


def start_watchdog(run_proxy_script=None, script_args=None, debug=False):
    watchdog_pid = os.fork()

    if watchdog_pid == 0:
        # os.setsid()
        logger = configure_watchdog_logger(debug)
        watchdog_pid_file = get_watchdog_pid_file()

        fd = None
        try:
            # Create the watchdog PID file in such a way that the proxy doesn't get run multiple times.
            fd = os.open(watchdog_pid_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

            # Read the existing watchdog PID file...
            with open(watchdog_pid_file, 'r') as fp:
                data = fp.read()
                watchdog_pid = int(data) if data else None

            if watchdog_pid:
                if is_process_alive(watchdog_pid):
                    # Looks like it's alive; let's exit the child process.
                    logger.info('Watchdog already running with pid=%d', watchdog_pid)
                    os._exit(0)
                else:
                    # Otherwise, the file was defunct; remove it and retry, letting errors be fatal.
                    logger.warning('Defunct proxy pid (%d) found; starting over', watchdog_pid)
                    unlink(watchdog_pid_file)
                    fd = os.open(watchdog_pid_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)

        watchdog_pid = os.getpid()
        os.write(fd, bytes(str(watchdog_pid)))
        os.close(fd)

        logger.info('Started watchdog with pid=%d', watchdog_pid)

        while True:
            start_proxy(run_proxy_script=run_proxy_script, script_args=script_args, debug=debug, proxy_logger=logger)
            os.wait()


def start_proxy(run_proxy_script=None, script_args=None, debug=False, proxy_logger=None):
    proxy_logger = proxy_logger or logging.getLogger('appdynamics.proxy')
    run_proxy_script = run_proxy_script or resource_filename('appdynamics_bindeps.proxy', 'runProxy')
    proxy_pid_file = get_proxy_pid_file()

    import appdynamics_proxysupport
    jre_dir = os.path.dirname(appdynamics_proxysupport.__file__)

    if os.path.exists(proxy_pid_file):
        with open(proxy_pid_file, "r") as fp:
            data = fp.read()
            proxy_pid = int(data) if data else None

        if proxy_pid and is_process_alive(proxy_pid):
            proxy_logger.warning('Using existing proxy with pid=%d', proxy_pid)
            return proxy_pid

        proxy_logger.warning('Found defunct proxy pid file with pid=%d', proxy_pid)
        os.unlink(proxy_pid_file)

    comm_dir = config.PROXY_CONTROL_PATH
    log_dir = config.LOGS_DIR
    runtime_dir = config.PROXY_RUN_DIR
    run_proxy_dir = os.path.dirname(run_proxy_script)

    command_args = [
        run_proxy_script,
        '-j', jre_dir,
        '-d', run_proxy_dir,
        '-r', runtime_dir,
        comm_dir,
        log_dir]
    command_args.extend(script_args or [])

    proxy_logger.info("Starting proxy: %s", ' '.join(command_args))
    proxy_pid = os.spawnvp(os.P_NOWAIT, run_proxy_script, command_args)

    # Make sure it comes up and stays up for at least a little while.
    time.sleep(PROXY_START_TIMEOUT)

    if not is_process_alive(proxy_pid):
        proxy_logger.warning('Failed to start proxy')
        raise CommandExecutionError('proxy did not start')
    else:
        proxy_logger.info('Started proxy with pid=%d', proxy_pid)

    with open(proxy_pid_file, "w") as fp:
        fp.write(str(proxy_pid))

    return proxy_pid


def stop_process(name, pid_file):
    try:
        with open(pid_file, 'r') as fp:
            pid = int(fp.read())

        if not is_process_alive(pid):
            os.unlink(pid_file)
            raise CommandExecutionError('%s not running -- removed stale pid file' % name)

        os.kill(pid, signal.SIGTERM)
        return pid
    except IOError:
        raise CommandExecutionError('%s not running or manually started' % name)


def configure_proxy_logger(debug):
    """Write logs to stdout.

    """

    logger = logging.getLogger('appdynamics.proxy')
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(default_log_formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def configure_watchdog_logger(debug):
    """Write logs to a log file.  Propagate to the root proxy logger.

    """

    logger = logging.getLogger('appdynamics.proxy.watchdog')
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(os.path.join(config.LOGS_DIR, 'watchdog.log'),
                                                   maxBytes=MAX_WATCHDOG_LOG_BYTES)
    handler.setLevel(level)
    handler.setFormatter(default_log_formatter)
    logger.addHandler(handler)
    return logger
