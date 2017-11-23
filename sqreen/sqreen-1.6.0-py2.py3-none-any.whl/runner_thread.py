# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen Python agent thread composition
"""
import atexit
import json
import os
import sys
import threading
import time
import traceback
from copy import copy
from logging import getLogger
from random import randint
from threading import Event, Thread

from .config import CONFIG
from .constants import CHANGELOG_URL, COMPATIBILITY_URL, STATUS_URL
from .deliverer import get_deliverer
from .exceptions import UnsupportedFrameworkVersion, UnsupportedPythonVersion
from .frameworks import django_framework, flask_framework, pyramid_framework
from .http_client import Urllib3Connection
from .instrumentation import Instrumentation
from .log import configure_root_logger
from .metadata import __version__
from .metrics import MetricsStore
from .remote_command import RemoteCommand
from .remote_exception import RemoteException
from .runner import (MAX_OBS_QUEUE_LENGTH, MAX_QUEUE_LENGTH, CappedQueue,
                     Runner, RunnerSettings, RunnerStop,
                     process_initial_commands)
from .runtime_infos import (RuntimeInfos, get_parent_cmdline,
                            get_process_cmdline)
from .session import InvalidToken, Session
from .utils import configure_raven_breadcrumbs

RUNNER_THREAD = None
RUNNER_THREAD_PID = None
RUNNER_LOCK = threading.Lock()

# Graceful timeout, max time waiting for the runner thread to exit before exiting
GRACEFUL_TIMEOUT = 4
GRACEFUL_FAIL_MSG = "Sqreen thread didn't exit after %s seconds"

LOGGER = getLogger(__name__)


def uwsgi_version_info():
    """Return uWSGI version tuple if run in uWSGI, None otherwise."""
    # Import must be delayed inside the function, because the uwsgi module is
    # not known by sqreen-start.
    try:
        import uwsgi
    except ImportError:
        return None
    else:
        return uwsgi.version_info


def quick_exit():
    """Check for early exit."""
    if os.environ.get('SQREEN_SKIP_LOGOUT', False):
        return True
    # uWSGI 2.0.15 may segfault upon exiting.
    # See https://github.com/unbit/uwsgi/issues/1651.
    uwsgi_vers = uwsgi_version_info()
    if uwsgi_vers and uwsgi_vers >= (2, 0, 15):
        return True
    elif 'django' in sys.modules:
        return django_framework.DjangoRequest.DEBUG_MODE
    elif 'flask' in sys.modules:
        return flask_framework.FlaskRequest.DEBUG_MODE
    elif 'pyramid' in sys.modules:
        return pyramid_framework.PyramidRequest.DEBUG_MODE
    return False


# Exit mechanism
def sqreen_exit(runner, queue):
    queue.put(RunnerStop)

    if quick_exit():
        LOGGER.warning("Quick exit, don't logout")
        return

    try:
        runner.join(GRACEFUL_TIMEOUT)
    except RuntimeError:
        logger = getLogger(__name__)
        logger.warning(GRACEFUL_FAIL_MSG, GRACEFUL_TIMEOUT)
    else:
        if runner.isAlive():
            logger = getLogger(__name__)
            logger.warning(GRACEFUL_FAIL_MSG, GRACEFUL_TIMEOUT)


def should_start_runner_thread():
    global RUNNER_THREAD
    global RUNNER_THREAD_PID

    runner_stopped = False
    if RUNNER_THREAD.runner and RUNNER_THREAD.runner.stop is True:
        runner_stopped = True

    return RUNNER_THREAD_PID != os.getpid() and RUNNER_THREAD.isAlive() is False and not runner_stopped


def before_hook_point():
    global RUNNER_THREAD
    global RUNNER_THREAD_PID

    if should_start_runner_thread():
        with RUNNER_LOCK:
            # The the current pid early to avoid starting the thread multiple
            # times
            RUNNER_THREAD_PID = os.getpid()

            if not should_start_runner_thread():
                LOGGER.info("The runner thread has already been started")

            runner = RunnerThread(RuntimeInfos().all())
            runner.queue = RUNNER_THREAD.queue
            runner.observations_queue = RUNNER_THREAD.observations_queue
            runner.instrumentation = RUNNER_THREAD.instrumentation
            runner.settings = RUNNER_THREAD.settings
            runner.start()

            atexit.register(sqreen_exit, runner=runner, queue=runner.queue)
            RUNNER_THREAD = runner

            LOGGER.info("Sucessfully started runner thread for pid: %d", os.getpid())


def _dump_thread_stacks():
    """ Try to dump all the currently running thread stacks
    """
    try:
        msg = ["Threads stacks \n"]
        thread_name_map = {thread.ident: thread.name for thread in threading.enumerate()}

        for thread_id, stack in sys._current_frames().items():
            msg.append("# Thread: id '%r', name %r" % (thread_id, thread_name_map[thread_id]))
            msg.append("".join(traceback.format_stack(stack)))

        LOGGER.debug("\n".join(msg))
    except Exception:
        LOGGER.exception("Something happened")


BLACKLISTED_COMMANDS = ['ipython', 'celery worker', 'rq worker', 'newrelic-admin', 'manage.py shell']


def start():
    """ Start the background thread and start protection
    """
    # Check if the agent is not disabled first
    try:
        disabled = int(os.getenv('SQREEN_DISABLE', 0))
    except ValueError:
        disabled = None

    # Configure logging
    configure_root_logger(CONFIG['LOG_LEVEL'], CONFIG['LOG_LOCATION'])

    # Retrieve the command used to launch the process
    command = get_process_cmdline()

    # Retrieve the parent command
    parent_command = get_parent_cmdline()

    # Check if we shouldn't launch ourselves
    for blacklisted_command in BLACKLISTED_COMMANDS:
        if blacklisted_command in command or blacklisted_command in parent_command:
            msg = 'Sqreen agent is disabled when running %s.'
            LOGGER.debug(msg, blacklisted_command)
            return

    if hasattr(sys, 'argv') and len(sys.argv) >= 2 and sys.argv[1] == 'test':
        LOGGER.debug('Sqreen agent is disabled when running tests.')
        return

    if disabled:
        LOGGER.debug('Sqreen agent is disabled.')
        return

    try:
        runtime_infos = RuntimeInfos().all()
    except UnsupportedFrameworkVersion as exception:
        msg = ("%s version %s is not supported in this agent version.\n"
               "Sqreen agent is disabled, you're not protected.\n"
               "Documentation can be found at %s.\n"
               "Changelog can be found at %s.")
        LOGGER.critical(msg, exception.framework.title(), exception.version,
                        COMPATIBILITY_URL, CHANGELOG_URL)
        # Alter os.environ?
        return
    except UnsupportedPythonVersion as exception:
        msg = ("Python version %s is not supported in this agent version.\n"
               "Sqreen agent is disabled, you're not protected.\n"
               "Documentation can be found at %s.\n"
               "Changelog can be found at %s.")
        LOGGER.critical(msg, exception.python_version,
                        COMPATIBILITY_URL, CHANGELOG_URL)
        return

    # Configure raven breadcrumbs at start
    configure_raven_breadcrumbs()

    global RUNNER_THREAD
    global RUNNER_THREAD_PID

    # Check for double instrumentation
    if RUNNER_THREAD is None:
        try:
            runner = RunnerThread(runtime_infos)
            runner.start()

            atexit.register(sqreen_exit, runner=runner, queue=runner.queue)

            timeout = runner.instrumentation_done.wait(10)

            if timeout is not True:
                msg = "Sqreen couldn't start. Check network connectivity: %s"
                LOGGER.critical(msg, STATUS_URL)

                # Also dump the stacktraces of all running threads
                _dump_thread_stacks()
            else:
                if runner.isAlive():
                    LOGGER.info("Sqreen instrumentation started successfully")
        except Exception:
            LOGGER.critical("Sqreen thread fails to start, you're not protected",
                            exc_info=True)
            return

        RUNNER_THREAD = runner
        RUNNER_THREAD_PID = os.getpid()
    else:
        runner = RUNNER_THREAD

    return runner


def get_session(url, token, proxy_url=None):
    """ Create a connection with the endpoint URL and a session. Returns only
    the session.
    """
    LOGGER.warning("Connection to %s%s", url, " using proxy %s" % proxy_url if proxy_url else "")
    con = Urllib3Connection(url, proxy_url)
    session = Session(con, token)
    return session


def get_initial_features(config_features, login_features):
    LOGGER.debug("Login features: %s", login_features)

    final_features = copy(login_features)

    if config_features:
        parsed_config_features = {}
        try:
            parsed_config_features = json.loads(config_features)
        except (ValueError, TypeError):
            LOGGER.warning("Invalid config initial features %s", config_features,
                           exc_info=True)

        if parsed_config_features and isinstance(parsed_config_features, dict):
            msg = "Override login initial features with %s"
            LOGGER.warning(msg, parsed_config_features)

            final_features.update(parsed_config_features)

            LOGGER.warning("Final features %s", final_features)

    return final_features


def get_runner(config, login_result, session, queue, runtime_infos, observation_queue, instrumentation, settings):
    initial_features = get_initial_features(config['INITIAL_FEATURES'],
                                            login_result.get('features', {}))

    # Get the right deliverer according to initial features
    deliverer = get_deliverer(initial_features.get('batch_size', 0),
                              initial_features.get('max_staleness', 0),
                              session)
    remote_command = RemoteCommand.with_production_commands()
    metrics_store = MetricsStore()
    metrics_store.register_production_aggregators()
    metrics_store.register_default_metrics()

    # Setup the runner
    runner = Runner(queue, observation_queue, session,
                    deliverer, remote_command, runtime_infos,
                    instrumentation, metrics_store, settings,
                    initial_features)
    return runner


class RunnerThread(Thread):
    """ Class responsible for starting the runner and monitor it
    """

    name = "SqreenRunnerThread"

    def __init__(self, runtime_infos):
        super(RunnerThread, self).__init__()
        self.daemon = True
        self.queue = CappedQueue(MAX_QUEUE_LENGTH)
        self.observations_queue = CappedQueue(MAX_OBS_QUEUE_LENGTH)
        self.instrumentation_done = Event()
        self.runtime_infos = runtime_infos
        self.instrumentation = Instrumentation(self.observations_queue, self.queue, before_hook_point)
        self.settings = RunnerSettings()
        self.runner = None
        self.started = False

    def run(self):
        """ Launch the runner
        """
        self.started = True
        LOGGER.debug('Starting Sqreen %s', __version__)
        # FIXME this part should be more tested
        while True:
            session = None
            self.runner = None

            try:
                try:
                    token = CONFIG['TOKEN']
                except KeyError:
                    msg = ("Sorry but we couldn't find your Sqreen token.\n"
                           "Your application is NOT currently protected by Sqreen.\n"
                           "\n"
                           "Have you filled your sqreen.ini?")
                    LOGGER.critical(msg)
                    self.instrumentation_done.set()
                    return

                LOGGER.warning("Using token %s", token)

                # Initiate HTTP connection to the backend and the session
                session = get_session(CONFIG['URL'], token, CONFIG['PROXY_URL'])

                runtime_infos = dict(self.runtime_infos)
                runtime_infos['various_infos'] = {
                    k: v for k, v in runtime_infos['various_infos'].items()
                    if k != 'dependencies'
                }
                try:
                    login_result = session.login(runtime_infos)
                except InvalidToken:
                    msg = ("Sorry but your Sqreen token appears to be invalid.\n"
                           "Your application is NOT currently protected by Sqreen.\n"
                           "\n"
                           "Please check the token against the interface")
                    LOGGER.critical(msg)
                    self.instrumentation_done.set()
                    return

                LOGGER.info("Login success")

                self.runner = get_runner(CONFIG, login_result, session, self.queue,
                                         self.runtime_infos, self.observations_queue,
                                         self.instrumentation, self.settings)

                # Process the initial commands
                process_initial_commands(login_result, self.runner)

                self.instrumentation_done.set()
                self.runner.run()
                # If the runner exit, returns
                return
            except Exception:
                LOGGER.exception("An unknown exception occured")

                if session is not None and session.is_connected():
                    try:
                        session.post_sqreen_exception(RemoteException(sys.exc_info()).to_dict())
                        session.logout()
                    except Exception:
                        LOGGER.exception("Exception while logout")
                        return

                try:
                    self.instrumentation.deinstrument_all()
                except Exception:
                    # We did not managed to remove instrumentation, state is unclear:
                    # terminate thread
                    LOGGER.exception("Exception while trying to clean-up")
                    return

                delay = randint(0, 10)
                LOGGER.debug("Sleeping %s seconds before retry", delay)
                time.sleep(delay)
