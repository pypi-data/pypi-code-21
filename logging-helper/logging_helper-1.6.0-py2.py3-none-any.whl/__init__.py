
# Get module version
from ._metadata import __version__

# Import key items from module
from .logging_helper import (setup_logging,
                             FATAL, fatal,
                             CRITICAL, critical,
                             ERROR, error,
                             WARNING, warning,
                             WARN, warn,
                             INFO, info, log,
                             DEBUG, debug,
                             NOTSET,
                             NullHandler,
                             getLevelName,
                             getLogger,
                             getLoggerClass,
                             setLoggerClass,
                             makeLogRecord,
                             ensure_path_exists,
                             setup_log_format,
                             check_for_main,
                             get_caller_filename,
                             get_caller_name)

__all__ = ['CRITICAL', 'DEBUG', 'ERROR', 'FATAL', 'INFO', 'NOTSET', 'WARN', 'WARNING',
           'critical', 'debug', 'error', 'exception', 'fatal', 'warn', 'warning', 'info', 'log',
           'NullHandler', 'getLevelName', 'getLogger', 'getLoggerClass', 'makeLogRecord', 'setLoggerClass',
           '__version__', 'setup_logging', 'ensure_path_exists', 'setup_log_format', 'check_for_main',
           'get_caller_filename', 'get_caller_name']

# Set default logging handler to avoid "No handler found" warnings.
getLogger(__name__).addHandler(NullHandler())
