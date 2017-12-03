#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Jan Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------


"""
This module provides base implementation of daemon service represented by the
:py:class:`pyzenkit.zendaemon.ZenDaemon` class. It builds on top of :py:mod:`pyzenkit.baseapp`
module and adds couple of other usefull features:

* Fully automated daemonization process.
* Event driven design.
* Support for handling arbitrary signals.
* Support for modularity with daemon components.


Daemonization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Daemonization is a process of transforming foreground application into a background
always running service. The :py:class:`pyzenkit.zendaemon.ZenDaemon` class has
this feature built in and configurable with command line options, or configuration
files/directories.

Daemonization is implemented on top of the :py:mod:`pyzenkit.daemonizer` utility
library, please refer to its documentation for more details.


Event driven design and event queue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The daemon application has the event driven design. The :py:func:`ZenDaemon._sub_stage_process`
method is implemented to perform an infinite event loop. There are events being emited
from different parts of the application, which are then being ordered into event queue.
Each of these events is then handled with appropriate callback method.

Event callback methods must be registered into daemon application to be recognized.
Multiple event callbacks my be registered for certain single event. In this case
those callbacks will be called in order of registration and a result of the previous
one will be passed as input of the next. In other words callbacks form a pipeline
and event will be pushed through that. Each callback method has the opportunity to
break the pipeline/chain by returning apropriate flag.

The naming convention for event callback method is the following:

* Event callback must be method, which accepts reference to :py:class:`ZenDaemon` ``daemon``
  as first argument and :py:class:`dict` ``args`` as second argument.
* Event callback method name must begin with ``cbk_event_`` prefix.
* Event name in method name after the prefix must also be `snake_cased``.

Note, that event name in callback method name is not used in any way for mapping
callbacks to events (like in the case of **actions**), the callbacks are explicitly
registered to handle particular events. It is however a great best practice and
it is very clear then which callback handles which event.

Following are examples of valid event callbacks::

    cbk_event_test(self, daemon, args)
    cbk_event_another_test(self, daemon, args)

Each daemon application has an instance of the :py:class:`EventQueueManager` as
public attribute, which represents the event queue. There are following methods
available for scheduling events into the queue:

* End of the queue: :py:func:`EventQueueManager.schedule`
* Beginning of the queue: :py:func:`EventQueueManager.schedule_next`
* After certain time interval: :py:func:`EventQueueManager.schedule_after`
* At specific time: :py:func:`EventQueueManager.schedule_at`


Signal handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each daemon service should be capable of receiving and handling external signals.
Currently support for following signals is built-in:

SIGINT
    Stop the infinite event loop and exit the application.

SIGHUP
    Reload configuration and reconfigure the application.

SIGUSR1
    Save current application runlog to JSON file.

SIGUSR2
    Save current application state to JSON file. Application state is a complete
    dump of the whole application.

Signals are catched by the daemon engine, transformed into high priority events and
these are then handled ASAP with following built-in event callbacks:

* :py:func:`ZenDaemon.cbk_event_signal_hup`
* :py:func:`ZenDaemon.cbk_event_signal_usr1`
* :py:func:`ZenDaemon.cbk_event_signal_usr2`

There are following built-in application actions, that can be used to send particular
signal to apropriate running daemon:

* :py:func:`ZenDaemon.cbk_action_signal_alrm`
* :py:func:`ZenDaemon.cbk_action_signal_check`
* :py:func:`ZenDaemon.cbk_action_signal_hup`
* :py:func:`ZenDaemon.cbk_action_signal_int`
* :py:func:`ZenDaemon.cbk_action_signal_usr1`
* :py:func:`ZenDaemon.cbk_action_signal_usr2`

These actions may be executed in a following way::

    path/to/zendaemon.py --action signal-usr1
    path/to/zendaemon.py --action=signal-usr2


Daemon components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The daemon components are actual workers in this paricular daemon design. The :py:class:`ZenDaemon`
class is in fact only a container for these components, that holds them all
together and provides a working environment. The actual real work is being done inside
these smaller components. They need to be registered inside the daemon to receive
the events and the daemon is then going through the event queue and executing correct
event callbacks inside these components.

Daemon components are also a great way for code reusability, because one can have
a library of usefull generic components and multiple daemons can be then implemented
very quickly by simply reusing them. For example one might implement component for
trailing text files and many different daemons might reuse that code and add some
additional functionality on top of that.


Module contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :py:class:`QueueEmptyException`
* :py:class:`ZenDaemonComponentException`
* :py:class:`ZenDaemonException`
* :py:class:`EventQueueManager`
* :py:class:`ZenDaemonComponent`
* :py:class:`ZenDaemon`
* :py:class:`DemoZenDaemonComponent`
* :py:class:`DemoZenDaemon`


Programming API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* public attributes:

    * :py:attr:`ZenDaemon.queue` - Event queue.

* public methods:

    * :py:func:`ZenDaemon.done` - Stop the infinite event loop and exit the application.
    * :py:func:`ZenDaemon.wait` - Pause the processing for given amount of time.
"""


__author__  = "Jan Mach <honza.mach.ml@gmail.com>"


import os
import re
import sys
import json
import time
import copy
import signal
import collections
import subprocess
import heapq
import math
import glob
import pprint

#
# Custom libraries.
#
import pyzenkit.baseapp
import pyzenkit.daemonizer


# Translation table to translate signal numbers to their names.
SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) \
    for n in dir(signal) if n.startswith('SIG') and '_' not in n )


def _json_default(obj):
    """
    Fallback method for serializing unknown objects into JSON.
    """
    if isinstance(obj, ZenDaemonComponent):
        return "COMPONENT({})".format(obj.__class__.__name__)
    if callable(obj):
        return "CALLBACK({}:{})".format(obj.__self__.__class__.__name__, obj.__name__)
    return repr(obj)


#-------------------------------------------------------------------------------


class QueueEmptyException(Exception):
    """
    Exception representing empty event queue. This exception will be thrown by
    :py:class:`zendaemon.EventQueueManager` in the event of empty event queue.
    """
    def __init__(self, description, **params):
        """
        Initialize new exception with given description and optional additional
        parameters.

        :param str description: Description of the problem.
        :param params: Optional additional parameters.
        """
        super().__init__()

        self.description = description
        self.params = params

    def __str__(self):
        """
        Operator override for automatic string output.
        """
        return repr(self.description)


class EventQueueManager:
    """
    Implementation of event queue manager. This implementation supports scheduling
    of both sequential events and timed events (events scheduled for specific time).
    The actual event object, that is added into the queue may be arbitrary object,
    there are no restrictions for its type or interface, because the queue manager
    does not interacts with the event itself. Internally two separate event queues
    are used, one for sequentialy scheduled events and another for timed events.
    For best performance the sequential queue is implemented using :py:class:`collections.dequeue`
    object and the timed queue is implemented using :py:mod:`heapq` module.
    """

    def __init__(self):
        """
        Base event queue manager constructor. Initialize internal event queues.
        """
        self.events    = collections.deque()
        self.events_at = []

    def schedule(self, event, args = None):
        """
        Schedule new event to the end of the event queue.

        :param event: Event to be scheduled.
        :param args: Optional event arguments to be stored alongside the event.
        """
        self.events.append((event, args))

    def schedule_next(self, event, args = None):
        """
        Schedule new event to the beginning of the event queue.

        :param event: Event to be scheduled.
        :param args: Optional event arguments to be stored alongside the event.
        """
        self.events.appendleft((event, args))

    def schedule_at(self, tstamp, event, args = None):
        """
        Schedule new event for a specific time.

        :param float tstamp: Timestamp to which to schedule the event (compatible with :py:func:`time.time`).
        :param event: Event to be scheduled.
        :param args: Optional event arguments to be stored alongside the event.
        """
        heapq.heappush(self.events_at, (tstamp, event, args))

    def schedule_after(self, delay, event, args = None):
        """
        Schedule new event after a given time delay.

        :param float delay: Time delay after which to schedule the event.
        :param event: Event to be scheduled.
        :param args: Optional event arguments to be stored alongside the event.
        """
        tstamp = time.time() + delay
        heapq.heappush(self.events_at, (tstamp, event, args))

    def next(self):
        """
        Fetch next event from queue.

        :raises QueueEmptyException: If the queue is empty.
        :return: Return next scheduled event from queue along with its optional arguments.
        :rtype: tuple
        """
        len1 = len(self.events_at)
        if len1:
            if self.events_at[0][0] <= time.time():
                (tstamp, event, args) = heapq.heappop(self.events_at)
                return (event, args)
        len2 = len(self.events)
        if len2:
            return self.events.popleft()
        if (len1 + len2) == 0:
            raise QueueEmptyException("Event queue is empty")
        return (None, None)

    def when(self):
        """
        Determine the timestamp of the next scheduled event.

        :return: Unix timestamp of next scheduled event.
        :rtype: float
        """
        if self.events:
            return time.time()
        return self.events_at[0][0]

    def wait(self):
        """
        Calculate the waiting period until the next event in queue is due.

        :return: Time interval for which to wait until the next event is due.
        :rtype: float
        """
        if self.events:
            return 0
        return self.events_at[0][0] - time.time()

    def count(self):
        """
        Count the total number of scheduled events.

        :return: Number of events.
        :rtype: int
        """
        return len(self.events_at) + len(self.events)


#-------------------------------------------------------------------------------


def calc_statistics(stats_cur, stats_prev, tdiff):
    """
    Calculate statistics.
    """
    result = {}
    for key in stats_cur:
        if isinstance(stats_cur[key], dict):
            result[key] = calc_statistics(stats_cur[key], stats_prev.get(key, {}), tdiff)
        else:
            result[key] = {
                # Absolute count.
                'cnt':  stats_cur[key],
                # Increase count (delta from previous value).
                'inc':  stats_cur[key] - stats_prev.get(key, 0),
                # Processing speed (#/s).
                'spd': (stats_cur[key] - stats_prev.get(key, 0)) / tdiff,
                # Percentage increase count.
                'pct': (stats_cur[key] - stats_prev.get(key, 0)) / (stats_cur[key] / 100)
            }
    return result


#-------------------------------------------------------------------------------


class ZenDaemonComponentException(pyzenkit.baseapp.ZenAppProcessException):
    """
    Describes problems specific to daemon components.
    """
    pass


class ZenDaemonComponent:
    """
    Base implementation for all daemon components. Daemon components are building
    blocks of each daemon and they are responsible for the actual work to be done.
    This approach enables very easy reusability.
    """

    def __init__(self, **kwargs):
        """
        Base daemon component object constructor.
        """
        self.statistics_cur  = {}
        self.statistics_prev = {}
        self.statistics_ts   = time.time()
        self.pattern_stats   = "{}\n\t{:15s}  {:12,d} (+{:8,d}, {:8,.2f} #/s)"

    def inc_statistic(self, key, increment = 1):
        """
        Raise given statistic key with given increment.
        """
        self.statistics_cur[key] = self.statistics_cur.get(key, 0) + increment

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        raise NotImplementedError("This method must be implemented in subclass")

    def get_state(self):
        """
        Get the current internal state of component (for debugging).
        """
        return {
            'statistics': self.statistics_cur
        }

    def get_statistics(self):
        """
        Calculate processing statistics
        """
        curts = time.time()
        tdiff = curts - self.statistics_ts

        stats = calc_statistics(self.statistics_cur, self.statistics_prev, tdiff)

        self.statistics_prev = copy.copy(self.statistics_cur)
        self.statistics_ts = curts
        return stats

    def setup(self, daemon):
        """
        Perform component setup.
        """
        pass

    def setup_dump(self, daemon):
        """
        Dump component setup.
        """
        pass


#-------------------------------------------------------------------------------


class ZenDaemonException(pyzenkit.baseapp.ZenAppProcessException):
    """
    Describes problems specific to daemons.
    """
    pass


class ZenDaemon(pyzenkit.baseapp.BaseApp):
    """
    Base implementation of generic daemon.
    """

    #
    # Class constants.
    #

    # Event loop processing flags.
    FLAG_CONTINUE = 1
    FLAG_STOP     = 0

    # List of event names.
    EVENT_SIGNAL_HUP     = 'signal_hup'
    EVENT_SIGNAL_USR1    = 'signal_usr1'
    EVENT_SIGNAL_USR2    = 'signal_usr2'
    EVENT_LOG_STATISTICS = 'log_statistics'

    # List of core configuration keys.
    CORE_STATE      = 'state'
    CORE_STATE_SAVE = 'save'

    # List of configuration keys.
    CONFIG_COMPONENTS     = 'components'
    CONFIG_NODAEMON       = 'no_daemon'
    CONFIG_CHROOT_DIR     = 'chroot_dir'
    CONFIG_WORK_DIR       = 'work_dir'
    CONFIG_PID_FILE       = 'pid_file'
    CONFIG_STATE_FILE     = 'state_file'
    CONFIG_UMASK          = 'umask'
    CONFIG_STATS_INTERVAL = 'stats_interval'
    CONFIG_PARALEL        = 'paralel'


    def __init__(self, **kwargs):
        """
        Default application object constructor.

        Only defines core internal variables. The actual object initialization,
        during which command line arguments and configuration files are parsed,
        is done during the configure() stage of the run() sequence. This method
        overrides the base implementation in :py:func:`baseapp.BaseApp.__init__`.

        :param kwargs: Various additional parameters.
        """
        super().__init__(**kwargs)

        self.flag_done  = False
        self.queue      = EventQueueManager()
        self.components = []
        self.callbacks  = {}

        self._init_callbacks(**kwargs)
        self._init_components(**kwargs)
        self._init_schedule(**kwargs)

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default application configurations. This method overrides the
        base implementation in :py:func:`baseapp.BaseApp._init_argparser` and it
        adds additional configurations via ``cfgs`` parameter.

        Gets called from main constructor :py:func:`BaseApp.__init__`.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_NODAEMON,       False),
            (self.CONFIG_CHROOT_DIR,     None),
            (self.CONFIG_WORK_DIR,       '/'),
            (self.CONFIG_PID_FILE,       os.path.join(self.paths.get(self.PATH_RUN), "{}.pid".format(self.name))),
            (self.CONFIG_STATE_FILE,     os.path.join(self.paths.get(self.PATH_RUN), "{}.state".format(self.name))),
            (self.CONFIG_UMASK,          0o002),
            (self.CONFIG_STATS_INTERVAL, 300),
            (self.CONFIG_PARALEL,        False),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _init_argparser(self, **kwargs):
        """
        Initialize application command line argument parser. This method overrides
        the base implementation in :py:func:`baseapp.BaseApp._init_argparser` and
        it must return valid :py:class:`argparse.ArgumentParser` object.

        Gets called from main constructor :py:func:`BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        :return: Initialized argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for common daemon arguments.
        #
        arggroup_daemon = argparser.add_argument_group('common daemon arguments')

        arggroup_daemon.add_argument('--no-daemon',      help = 'do not fully daemonize and stay in foreground (flag)', action='store_true', default = None)
        arggroup_daemon.add_argument('--chroot-dir',     help = 'name of the chroot directory', type = str, default = None)
        arggroup_daemon.add_argument('--work-dir',       help = 'name of the process work directory', type = str, default = None)
        arggroup_daemon.add_argument('--pid-file',       help = 'name of the pid file', type = str, default = None)
        arggroup_daemon.add_argument('--state-file',     help = 'name of the state file', type = str, default = None)
        arggroup_daemon.add_argument('--umask',          help = 'default file umask', default = None)
        arggroup_daemon.add_argument('--stats-interval', help = 'processing statistics display interval in seconds', type = int)
        arggroup_daemon.add_argument('--paralel',        help = 'run in paralel mode (flag)', action = 'store_true', default = None)

        return argparser

    def _init_event_callback(self, event, callback, prepend = False):
        """
        Set given callback as handler for given event.
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        if not prepend:
            self.callbacks[event].append(callback)
        else:
            self.callbacks[event].insert(0, callback)

    def _init_callbacks(self, **kwargs):
        """
        Initialize internal event callbacks.
        """
        for event in self.get_events():
            self.dbgout("Initializing event callback '{}':'{}'".format(str(event['event']), str(event['callback'])))
            self._init_event_callback(event['event'], event['callback'], event['prepend'])

    def _init_components(self, **kwargs):
        """
        Initialize daemon components.
        """
        components = kwargs.get(self.CONFIG_COMPONENTS, [])
        for component in components:
            self.components.append(component)
            elist = component.get_events()
            for event in elist:
                self._init_event_callback(event['event'], event['callback'], event['prepend'])

    def _init_schedule(self, **kwargs):
        """
        Schedule initial events.
        """
        initial_events = kwargs.get('schedule', [])
        for event in initial_events:
            self.queue.schedule(*event)
        initial_events = kwargs.get('schedule_next', [])
        for event in initial_events:
            self.queue.schedule_next(*event)
        initial_events = kwargs.get('schedule_at', [])
        for event in initial_events:
            self.queue.schedule_at(*event)
        initial_events = kwargs.get('schedule_after', [])
        for event in initial_events:
            self.queue.schedule_after(*event)


    #---------------------------------------------------------------------------


    def _configure_postprocess(self):
        """
        Perform configuration postprocessing and calculate core configurations.
        This method overrides the base implementation in :py:func:`baseapp.BaseApp._configure_postprocess`.

        Gets called from :py:func:`BaseApp._stage_setup_configuration`.
        """
        super()._configure_postprocess()

        ccfg = {}
        ccfg[self.CORE_STATE_SAVE]  = True
        self.config[self.CORE][self.CORE_STATE] = ccfg

        if self.c(self.CONFIG_NODAEMON):
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOCONS] = True
            self.dbgout("Console log output is enabled via '--no-daemon' configuration")
        else:
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOCONS] = False

        self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = True
        self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = True
        self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = True

    def _sub_stage_setup(self):
        """
        **SUBCLASS HOOK**: Perform additional custom setup actions in **setup** stage.

        Gets called from :py:func:`BaseApp._stage_setup` and it is a **SETUP SUBSTAGE 06**.
        """
        for component in self.components:
            self.dbgout("Configuring daemon component '{}'".format(component))
            component.setup(self)

    def _stage_setup_dump(self):
        """
        Dump script setup information.

        This method will display information about script system paths, configuration
        loaded from CLI arguments or config file, final merged configuration.
        """
        super()._stage_setup_dump()

        self.logger.debug("Daemon component list >>>\n%s", json.dumps(self.components, sort_keys=True, indent=4, default=_json_default))
        self.logger.debug("Registered event callbacks >>>\n%s", json.dumps(self.callbacks, sort_keys=True, indent=4, default=_json_default))
        self.logger.debug("Daemon component setup >>>\n")
        for component in self.components:
            self.logger.debug(">>> %s >>>\n", component.__class__.__name__)
            component.setup_dump(self)


    #---------------------------------------------------------------------------


    def _hnd_signal_wakeup(self, signum, frame):
        """
        Signal handler - wakeup after sleep/pause.
        """
        self.logger.info("Received wakeup signal (%s)", signum)

    def _hnd_signal_hup(self, signum, frame):
        """
        Signal handler - **SIGHUP**

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event ``signal_hup``.
        """
        self.logger.warning("Received signal 'SIGHUP' (%s)", signum)
        self.queue.schedule_next(self.EVENT_SIGNAL_HUP)

    def _hnd_signal_usr1(self, signum, frame):
        """
        Signal handler - **SIGUSR1**

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event ``signal_usr1``.
        """
        self.logger.info("Received signal 'SIGUSR1' (%s)", signum)
        self.queue.schedule_next(self.EVENT_SIGNAL_USR1)

    def _hnd_signal_usr2(self, signum, frame):
        """
        Signal handler - **SIGUSR2**

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event ``signal_usr2``.
        """
        self.logger.info("Received signal 'SIGUSR2' (%s)", signum)
        self.queue.schedule_next(self.EVENT_SIGNAL_USR2)


    #---------------------------------------------------------------------------


    def cbk_event_signal_hup(self, daemon, args = None):
        """
        Event callback for handling signal - **SIGHUP**

        .. todo::

            In the future this signal should be responsible for soft restart of
            daemon process. Currently work in progress.
        """
        self.logger.warning("Handling event for signal 'SIGHUP'")
        return (self.FLAG_CONTINUE, args)

    def cbk_event_signal_usr1(self, daemon, args = None):
        """
        Event callback for handling signal - **SIGUSR1**

        This signal forces the daemon process to save the current runlog to JSON
        file.
        """
        self.logger.info("Handling event for signal 'SIGUSR1'")
        self._utils_runlog_save(self.runlog)
        return (self.FLAG_CONTINUE, args)

    def cbk_event_signal_usr2(self, daemon, args = None):
        """
        Event callback for handling signal - **SIGUSR2**

        This signal forces the daemon process to save the current state to JSON
        file. State is more verbose than runlog and it contains almost all
        internal data.
        """
        self.logger.info("Handling event for signal 'SIGUSR2'")
        if self.c(self.CONFIG_NODAEMON):
            self._utils_state_dump(self._get_state())
        else:
            self._utils_state_save(self._get_state())
        return (self.FLAG_CONTINUE, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        self.queue.schedule_after(self.c(self.CONFIG_STATS_INTERVAL), self.EVENT_LOG_STATISTICS)
        return (self.FLAG_CONTINUE, args)

    #---------------------------------------------------------------------------

    def send_signal(self, sign):
        """
        Send given signal to all currently running daemon(s).
        """
        pid = None
        try:
            pidfl = None # PID file list
            if not self.c(self.CONFIG_PARALEL):
                pidfl = [self._get_fn_pidfile()]
            else:
                pidfl = self._pidfiles_list()

            for pidfn in pidfl:
                pid = pyzenkit.daemonizer.read_pid(pidfn)
                if pid:
                    print("Sending signal '{}' to process '{}' [{}]".format(SIGNALS_TO_NAMES_DICT.get(sign, sign), pid, pidfn))
                    os.kill(pid, sign)

        except FileNotFoundError:
            print("PID file '{}' does not exist".format(self.c(self.CONFIG_PID_FILE)))

        except ValueError:
            print("Malformed PID file '{}'".format(self.c(self.CONFIG_PID_FILE)))

        except ProcessLookupError:
            print("Process with PID '{}' does not exist".format(pid))

        except PermissionError:
            print("Insufficient permissions to send signal '{}' to process '{}'".format(SIGNALS_TO_NAMES_DICT.get(sign, sign), pid))

    def cbk_action_signal_check(self):
        """
        Send signal '0' to currently running daemon.
        """
        self.send_signal(0)

    def cbk_action_signal_alrm(self):
        """
        Send signal 'SIGALRM' to currently running daemon.
        """
        self.send_signal(signal.SIGALRM)

    def cbk_action_signal_int(self):
        """
        Send signal 'SIGINT' to currently running daemon.
        """
        self.send_signal(signal.SIGINT)

    def cbk_action_signal_hup(self):
        """
        Send signal 'SIGHUP' to currently running daemon.
        """
        self.send_signal(signal.SIGHUP)

    def cbk_action_signal_usr1(self):
        """
        Send signal 'SIGUSR1' to currently running daemon.
        """
        self.send_signal(signal.SIGUSR1)

    def cbk_action_signal_usr2(self):
        """
        Send signal 'SIGUSR2' to currently running daemon.
        """
        self.send_signal(signal.SIGUSR2)


    #---------------------------------------------------------------------------


    def _get_state(self):
        """
        Get current daemon state.
        """
        state = {
            'time':           time.time(),
            'rc':             self.retc,
            'config':         self.config,
            'paths':          self.paths,
            'pstate':         self.pstate,
            'callbacks':      self.callbacks,
            'component_list': self.components,
            'components':     {},
            'runlog':         self.runlog,
        }
        for component in self.components:
            state['components'][component.__class__.__name__] = component.get_state(self)
        return state

    def _get_statistics(self):
        """
        Get current daemon statistics.
        """
        statistics = {
            'time':           time.time(),
            'components':     {},
        }
        for component in self.components:
            statistics['components'][component.__class__.__name__] = component.get_statistics(self)
        return statistics

    def _utils_state_dump(self, state):
        """
        Dump current daemon state.

        Dump current daemon state to terminal (JSON).
        """
        # Dump current script state.
        #self.logger.debug("Current daemon state >>>\n{}".format(json.dumps(state, sort_keys=True, indent=4)))
        print("Current daemon state >>>\n{}".format(self.json_dump(state, default=_json_default)))

    def _utils_state_log(self, state):
        """
        Dump current daemon state.

        Dump current daemon state to terminal (JSON).
        """
        # Dump current script state.
        #self.logger.debug("Current daemon state >>>\n{}".format(json.dumps(state, sort_keys=True, indent=4)))
        print("Current daemon state >>>\n{}".format(self.json_dump(state, default=_json_default)))

    def _utils_state_save(self, state):
        """
        Save current daemon state.

        Save current daemon state to external file (JSON).
        """
        sfn = self._get_fn_state()
        self.dbgout("Saving current daemon state to file '{}'".format(sfn))
        pprint.pprint(state)
        self.dbgout("Current daemon state:\n{}".format(self.json_dump(state, default=_json_default)))
        self.json_save(sfn, state, default=_json_default)
        self.logger.info("Current daemon state saved to file '%s'", sfn)

    def _pidfiles_list(self, **kwargs):
        """
        List all available pidfiles.
        """
        reverse = kwargs.get('reverse', False)
        pfn = os.path.join(self.paths['run'], '{}*.pid'.format(self.name))
        return sorted(glob.glob(pfn), reverse = reverse)

    def _get_fn_state(self):
        """
        Return the name of the state file for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return self.c(self.CONFIG_STATE_FILE)

        sfn = re.sub(r'\.state$',".{:05d}.state".format(os.getpid()), self.c(self.CONFIG_STATE_FILE))
        self.dbgout("Paralel mode: using '{}' as state file".format(sfn))
        return sfn

    def _get_fn_pidfile(self):
        """
        Return the name of the pidfile for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return self.c(self.CONFIG_PID_FILE)

        pfn = re.sub(r'\.pid$',".{:05d}.pid".format(os.getpid()), self.c(self.CONFIG_PID_FILE))
        self.dbgout("Paralel mode: using '{}' as pid file".format(pfn))
        return pfn

    def _get_fn_runlog(self):
        """
        Return the name of the runlog file for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.runlog".format(self.runlog[self.RLKEY_TSFSF]))

        rfn = os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.{:05d}.runlog".format(self.runlog[self.RLKEY_TSFSF], os.getpid()))
        self.dbgout("Paralel mode: using '{}' as runlog file".format(rfn))
        return rfn


    #---------------------------------------------------------------------------


    def get_events(self):
        """
        Get list of internal event callbacks.
        """
        return [
            { 'event': self.EVENT_SIGNAL_HUP,     'callback': self.cbk_event_signal_hup,     'prepend': False },
            { 'event': self.EVENT_SIGNAL_USR1,    'callback': self.cbk_event_signal_usr1,    'prepend': False },
            { 'event': self.EVENT_SIGNAL_USR2,    'callback': self.cbk_event_signal_usr2,    'prepend': False },
            { 'event': self.EVENT_LOG_STATISTICS, 'callback': self.cbk_event_log_statistics, 'prepend': False },
        ]

    def wait(self, period):
        """
        Wait/pause for given amount of seconds.
        """
        period = math.ceil(period)
        if period > 0:
            self.logger.info("Waiting for '%d' seconds until next scheduled event", period)
            signal.signal(signal.SIGALRM, self._hnd_signal_wakeup)
            signal.alarm(period)
            signal.pause()
            signal.alarm(0)

    def done(self):
        """
        Set the DONE flag to True.
        """
        self.flag_done = True

    def _daemonize(self):
        """
        Perform daemonization.
        """
        # Perform full daemonization
        if not self.c(self.CONFIG_NODAEMON):
            self.dbgout("Performing full daemonization")
            self.logger.info("Performing full daemonization")

            logs = pyzenkit.daemonizer.get_logger_files(self.logger)
            pyzenkit.daemonizer.daemonize(
                chroot_dir     = self.c(self.CONFIG_CHROOT_DIR),
                work_dir       = self.c(self.CONFIG_WORK_DIR),
                pid_file       = self._get_fn_pidfile(),
                umask          = self.c(self.CONFIG_UMASK),
                files_preserve = logs,
                signals        = {
                    signal.SIGHUP:  self._hnd_signal_hup,
                    signal.SIGUSR1: self._hnd_signal_usr1,
                    signal.SIGUSR2: self._hnd_signal_usr2,
                },
            )

            self.logger.info("Full daemonization done")
            self.runlog[self.RLKEY_PID] = os.getpid()

        # Perform simple daemonization
        else:
            self.dbgout("Performing simple daemonization")
            self.logger.info("Performing simple daemonization")

            pyzenkit.daemonizer.daemonize_lite(
                chroot_dir     = self.c(self.CONFIG_CHROOT_DIR),
                work_dir       = self.c(self.CONFIG_WORK_DIR),
                pid_file       = self._get_fn_pidfile(),
                umask          = self.c(self.CONFIG_UMASK),
                signals        = {
                    signal.SIGHUP:  self._hnd_signal_hup,
                    signal.SIGUSR1: self._hnd_signal_usr1,
                    signal.SIGUSR2: self._hnd_signal_usr2,
                },
            )

            self.logger.info("Simple daemonization done")
            self.runlog[self.RLKEY_PID] = os.getpid()

    def _event_loop(self):
        """
        Main event processing loop.
        """
        self.flag_done = False
        while not self.flag_done:
            try:
                (event, args) = self.queue.next()
                if event:
                    if event not in self.callbacks:
                        raise ZenDaemonException("There is no callback to handle event '{}'".format(event))
                    for handler in self.callbacks[event]:
                        (flag, args) = handler(self, args)
                        if flag != self.FLAG_CONTINUE:
                            break
                else:
                    wait_time = self.queue.wait()
                    if wait_time > 0:
                        self.wait(wait_time)

            except QueueEmptyException:
                self.logger.info("Event queue is empty, terminating")
                self.flag_done = True

    def _sub_stage_process(self):
        """
        **SUBCLASS HOOK**: Perform some actual processing in **process** stage.
        """

        try:
            self._daemonize()
            self._event_loop()

        except KeyboardInterrupt:
            pass

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except pyzenkit.baseapp.ZenAppProcessException as exc:
            self.error("ZenAppProcessException: {}".format(exc))

        except pyzenkit.baseapp.ZenAppException as exc:
            self.error("ZenAppException: {}".format(exc))

        except:
            (exct, excv, exctb) = sys.exc_info()
            self.error("Exception: {}".format(excv), trcb = exctb)

class DemoDaemonComponent(ZenDaemonComponent):
    """
    Minimalistic class for demonstration purposes.
    """

    def get_events(self):
        """
        Get list of internal event callbacks.
        """
        return [
            { 'event': 'default', 'callback': self.cbk_event_default, 'prepend': False }
        ]

    def cbk_event_default(self, daemon, args = None):
        """
        Callback handler for default event.
        """
        daemon.queue.schedule('default')
        daemon.logger.info("Working...")
        self.inc_statistic('cnt_default')
        time.sleep(1)
        daemon.logger.info("Work unit done")
        return (daemon.FLAG_CONTINUE, None)

class DemoZenDaemon(ZenDaemon):
    """
    Minimalistic class for demonstration purposes.
    """
    def __init__(self, name = None, description = None):
        """
        Initialize demonstration script. This method overrides the base
        implementation in :py:func:`baseapp.BaseApp.__init__` and it aims to
        even more simplify the script object creation.

        :param str name: Optional script name.
        :param str description: Optional script description.
        """
        name        = 'demo-zendaemon.py' if not name else name
        description = 'DemoZenDaemon - Demonstration daemon' if not description else description

        super().__init__(
            name        = name,
            description = description,

            #
            # Configure required application paths to harmless locations.
            #
            path_bin = '/tmp',
            path_cfg = '/tmp',
            path_log = '/tmp',
            path_tmp = '/tmp',
            path_run = '/tmp',

            # Force dhe demonstration daemon to stay in foreground.
            default_no_daemon = True,

            # Define internal daemon components.
            components = [
                DemoDaemonComponent()
            ],

            # Schedule initial daemon events.
            schedule = [
                ('default',)
            ]
        )

#-------------------------------------------------------------------------------

#
# Perform the demonstration.
#
if __name__ == "__main__":

    # Prepare demonstration environment.
    DMN_NAME = 'demo-zendaemon.py'
    pyzenkit.baseapp.BaseApp.json_save('/tmp/{}.conf'.format(DMN_NAME), {'test_a':1})
    try:
        os.mkdir('/tmp/{}'.format(DMN_NAME))
    except FileExistsError:
        pass

    ZENDAEMON = DemoZenDaemon(DMN_NAME)
    ZENDAEMON.run()
