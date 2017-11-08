import logging

from .constants import (
    LOG_LEVEL, LOG_HANDLER, ALL_LOGS, LOG_FORMATTER
)

if hasattr(logging, "NullHandler"):
    from logging import NullHandler
else:
    # Copied from Python 2.7.
    class NullHandler(logging.Handler):
        """
        This handler does nothing. It's intended to be used to avoid the
        "No handlers could be found for logger XXX" one-off warning. This is
        important for library code, which may contain code to log events. If a user
        of the library does not configure logging, the one-off warning might be
        produced; to avoid this, the library developer simply needs to instantiate
        a NullHandler and add it to the top-level logger of the library module or
        package.
        """
        def handle(self, record):
            pass
    
        def emit(self, record):
            pass
    
        def createLock(self):
            self.lock = None

def set_log_level(loglevel='WARNING'):
    global LOG_HANDLER;
    global ALL_LOGS;
    global LOG_LEVEL;

    if hasattr(logging, loglevel.upper()):
        level = getattr(logging, loglevel.upper())
        LOG_LEVEL = level
        LOG_HANDLER.setLevel(level)

        for logname, logger in ALL_LOGS.items():
            logger.setLevel(level)
    else:
        # XXX a warning.warn() should be raised. 
        pass

def add_handler(hdlr):
    global ALL_LOGS;

    ALL_LOGS['root'].addHandler(hdlr)

def get_logger(logname, level="", file_name=""):
    global LOG_HANDLER;
    global LOG_FORMATTER;
    global ALL_LOGS;

    if not LOG_HANDLER:
        LOG_HANDLER = NullHandler()
        formatter = logging.Formatter(LOG_FORMATTER)
        LOG_HANDLER.setFormatter(formatter)
        root_logger = logging.getLogger("batchcompute")
        root_logger.addHandler(LOG_HANDLER)
        ALL_LOGS['root'] = root_logger

    logger = None
    if logname in ALL_LOGS:
        logger = ALL_LOGS[logname]
    else:
        logger = logging.getLogger(logname) 
        logger.setLevel(LOG_LEVEL)
        ALL_LOGS[logname] = logger

    if file_name:
        LOG_HANDLER = logging.FileHandler(file_name) 
        LOG_HANDLER.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(LOG_FORMATTER)
        LOG_HANDLER.setFormatter(formatter)
        add_handler(LOG_HANDLER)

    if level:
        set_log_level(level)
    return logger 
