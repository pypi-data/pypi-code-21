#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import logging
import logging.handlers
import multiprocessing
import sys


DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


loggers_set = set()


mq = multiprocessing.Queue()


try:
    from logging.handlers import QueueHandler
except ImportError:
    # We are in python2 code
    class QueueHandler(logging.Handler):
        """
        This handler sends events to a queue. Typically, it would be used
        together with a multiprocessing Queue to centralise logging to file
        in one process (in a multi-process application), so as to avoid file
        write contention between processes.

        This code is new in Python 3.2, but this class can be copy pasted into
        user code for use with earlier Python versions.
        """

        # Copy-pasted as per above docstring from logging

        def __init__(self, queue):
            logging.Handler.__init__(self)
            self.queue = queue

        def enqueue(self, record):
            self.queue.put_nowait(record)

        def prepare(self, record):
            self.format(record)
            record.msg = record.message
            record.args = None
            record.exc_info = None
            return record

        def emit(self, record):
            try:
                self.enqueue(self.prepare(record))
            except Exception:
                self.handleError(record)

try:
    from logging.handlers import QueueListener
except ImportError:
    # We are in python2 code
    import threading
    try:
        import Queue
    except ImportError:
        # Make it pythonX with 3.0 <= X <3.2
        import queue as Queue

    class QueueListener(object):
        """
        This class implements an internal threaded listener which watches for
        LogRecords being added to a queue, removes them and passes them to a
        list of handlers for processing.
        """

        # Also copy-pasted
        _sentinel = None

        def __init__(self, queue, respect_handler_level=False, *handlers):
            self.queue = queue
            self.handlers = handlers
            self._stop = threading.Event()
            self._thread = None
            self.respect_handler_level = respect_handler_level

        def dequeue(self, block):
            return self.queue.get(block)

        def start(self):
            self._thread = t = threading.Thread(target=self._monitor)
            t.setDaemon(True)
            t.start()

        def prepare(self , record):
            return record

        def handle(self, record):
            record = self.prepare(record)
            for handler in self.handlers:
                if not self.respect_handler_level:
                    process = True
                else:
                    process = record.levelno >= handler.level
                if process:
                    handler.handle(record)

        def _monitor(self):
            q = self.queue
            has_task_done = hasattr(q, 'task_done')
            while not self._stop.isSet():
                try:
                    record = self.dequeue(True)
                    if record is self._sentinel:
                        break
                    self.handle(record)
                    if has_task_done:
                        q.task_done()
                except Queue.Empty:
                    pass
            # There might still be records in the queue.
            while True:
                try:
                    record = self.dequeue(False)
                    if record is self._sentinel:
                        break
                    self.handle(record)
                    if has_task_done:
                        q.task_done()
                except Queue.Empty:
                    break

        def enqueue_sentinel(self):
            self.queue.put_nowait(self._sentinel)

        def stop(self):
            self._stop.set()
            self.enqueue_sentinel()
            self._thread.join()
            self._thread = None


class RumbaFormatter(logging.Formatter):
    """The logging.Formatter subclass used by Rumba"""

    level_name_table = {
        'CRITICAL': 'CRT',
        'ERROR': 'ERR',
        'WARNING': 'WRN',
        'INFO': 'INF',
        'DEBUG': 'DBG'
    }

    def __init__(self):
        super(RumbaFormatter, self).__init__(
            fmt='%(asctime)s | %(levelname)3.3s | '
                '%(name)11.11s | %(message)s',
            datefmt='%H:%M:%S')

    def format(self, record):
        record.name = record.name.split('.')[-1]
        record.levelname = self.level_name_table[record.levelname]
        return super(RumbaFormatter, self).format(record)


def setup():
    """Configures the logging framework with default values."""
    global mq
    queue_handler = QueueHandler(mq)
    queue_handler.setLevel(logging.DEBUG)
    logging.basicConfig(handlers=[queue_handler], level=logging.DEBUG)
    logging.getLogger('').setLevel(logging.ERROR)
    logging.getLogger('rumba').setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = RumbaFormatter()
    handler.setFormatter(formatter)
    listener = QueueListener(mq, handler)
    listener.start()


# Used for the first call, in order to configure logging
def _get_logger_with_setup(name):
    setup()
    # Swap _get_logger implementation to the setup-less version.
    global _get_logger
    _get_logger = _get_logger_without_setup
    return logging.getLogger(name)


# Then this one is used.
def _get_logger_without_setup(name):
    return logging.getLogger(name)


_get_logger = _get_logger_with_setup


def get_logger(name):
    """
    Returns the logger named <name>.
    <name> should be the module name, for consistency. If setup has not been
    called yet, it will call it first.
    :param name: the name of the desired logger
    :return: The logger
    """
    return _get_logger(name)


def set_logging_level(level, name=None):
    """
    Set the current logging level to <level> for logger named <name>.
    If name is not specified, sets the logging level for all rumba loggers.
    Accepted levels are:
        DEBUG == 10,
        INFO == 20,
        WARNING == 30,
        ERROR == 40,
        CRITICAL == 50,
        NOTSET == 0
    (resets the logger: its level is set to the default or its parents' level)
    :param level: the desired logging level.
    :param name: The name of the logger to configure
    """
    if name is None:
        if level == 'NOTSET' or level == 0:
            set_logging_level(logging.INFO)
            return
        name = 'rumba'
    if (level == 'NOTSET' or level == 0) and name == '':
        set_logging_level(logging.ERROR, '')
        return
    logger = get_logger(name)
    loggers_set.add(logger)
    logger.setLevel(level)


def reset_logging_level():
    """
    Resets the current logging levels to the defaults.
    Defaults are: rumba           -> INFO,
                  everything else -> ERROR
    """
    # Un-sets every logger previously set
    for logger in loggers_set:
        logger.setLevel(logging.NOTSET)
    set_logging_level(logging.INFO)
    set_logging_level(logging.ERROR, '')
