'''
Logging module. Adds a stdout pipe to print stuff on the console.
'''

import sys
import logging
from copy import copy

LOGGER_KEY = 'HARBOR'


def init_logger():
    ''' Setup logger '''

    # It doesnt create new instances, just returns same logger under the closure.
    # Its fine to call it multiple times.
    instance = logging.getLogger(LOGGER_KEY)

    # Set loglevel to debug.
    instance.setLevel(logging.DEBUG)

    # Add a log pipe to stdout. StreamHandler appends, doesn't replace.
    logtostdout = logging.StreamHandler(sys.stdout)
    logtostdout.setLevel(logging.DEBUG)

    # Format for logs.
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    logtostdout.setFormatter(formatter)

    # Add stdout log to main logger instance.
    instance.addHandler(logtostdout)

    # Add some colors to log based on loglevel.
    if not sys.platform.startswith("win") and sys.stderr.isatty():
        def add_color_emit_ansi(func):
            """Add methods we need to the class."""
            def new(*args):
                """Method overload."""
                if len(args) == 2:
                    new_args = (args[0], copy(args[1]))
                else:
                    new_args = (args[0], copy(args[1]), args[2:])

                if hasattr(args[0], 'baseFilename'):
                    return func(*args)

                levelno = new_args[1].levelno

                if levelno >= 50:
                    color = '\x1b[31;5;7m\n '  # blinking red with black
                elif levelno >= 40:
                    color = '\x1b[31m'  # red
                elif levelno >= 30:
                    color = '\x1b[33m'  # yellow
                elif levelno >= 20:
                    color = '\x1b[32m'  # green
                elif levelno >= 10:
                    color = '\x1b[35m'  # pink
                else:
                    color = '\x1b[0m'  # normal

                new_args[1].msg = color + str(new_args[1].msg) + ' \x1b[0m'
                return func(*new_args)
            return new
        # all non-Windows platforms support ANSI Colors so we use them
        logging.StreamHandler.emit = add_color_emit_ansi(
            logging.StreamHandler.emit)

    return instance


def logger():
    ''' Get a logger instance. '''
    return logging.getLogger(LOGGER_KEY)
