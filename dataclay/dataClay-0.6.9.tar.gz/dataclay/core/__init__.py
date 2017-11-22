"""Internal module used by both client and servers.

The classes and functions in the dataClay module are available (when this
makes sense) to both the dataClay client and the Python dataClay Execution
Environment.

The "client" version is available at `dataclay` package, which works as en entry
point for all the common user-friendly functions.
"""
from contextlib import contextmanager
from distutils.util import strtobool
import logging
import logging.config
import os

from .paraver import PrvManager

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

prv = None

# Manually forcing the dataclay root logger here
logger = logging.getLogger("dataclay")

TRACE_ENABLED = strtobool(os.getenv("PARAVER_TRACE_ENABLED", "True"))
TRACE_OUTPUT = os.getenv("PARAVER_TRACE_OUTPUT", "/tmp/output")


###################################################################
# We like to have a little bit more of finesse wrt debug levels

# for lower-than-debug messages
TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

# for higher-than-debug but not printed by default
VERB_LEVEL_NUM = 15
logging.addLevelName(VERB_LEVEL_NUM, "VERBOSE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


def verbose(self, message, *args, **kws):
    if self.isEnabledFor(VERB_LEVEL_NUM):
        self._log(VERB_LEVEL_NUM, message, args, **kws)


# And monkey patch the logging library also
logging.TRACE = TRACE_LEVEL_NUM
logging.VERB = VERB_LEVEL_NUM
logging.Logger.verb = verbose
logging.Logger.verbose = verbose
logging.Logger.trace = trace


def initialize():
    """Initialize the dataClay frame (logging, tracing and constants).

    The caller should, prior to this initialize, set the ConfigOptions to valid
    values. After this initialize, the dataClay library is ready to go.
    """
    global prv
    if prv is not None:
        logger.error("Initialize function should be called once per run")

    debug = strtobool(os.getenv('DEBUG', "False"))

    config_kwargs = {
        "level": logging.DEBUG if debug else logging.INFO,
        "datefmt": "%H:%M:%S",  # I don't know how to add milliseconds here, doing it in the `format`
        "format": "%(asctime)s,%(msecs)03d %(levelname)-7s | %(name)s - %(message)s",
    }

    file_output = os.getenv('DATACLAY_LOGGING_FILE')
    if file_output:
        config_kwargs.update(filename=file_output, filemode='w')

    logging.basicConfig(**config_kwargs)
    logger.info("Starting dataClay library")
    logger.debug("Debug output seems to be enabled")

    # ToDo: Now TRACE_ENABLED seems to be true in a lot of situations. That should be looked into
    if TRACE_ENABLED:
        full_name = "{:s}-{:d}.prv".format(TRACE_OUTPUT, os.getpid())
        logger.verbose("Paraver tracing will be stored in file %s", full_name)
        prv = PrvManager(full_name)


@contextmanager
def size_tracking(io_file):
    """Track the bytes written into a certain seekable I/O file.
    :param io_file: The I/O file being written inside the with statement.
    """
    # Hack a little bit a circular import
    from dataclay.core import primitives

    start_track = io_file.tell()
    primitives.Int(32).write(io_file, 0)
    start_data = io_file.tell()
    yield
    end_data = io_file.tell()
    io_file.seek(start_track)
    primitives.Int(32).write(io_file, end_data - start_data)
    io_file.seek(end_data)
