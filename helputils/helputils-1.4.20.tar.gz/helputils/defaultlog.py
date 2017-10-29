"""defaultlog.py - In a seperate module to prevent circular imports."""
from logging import getLogger
from logging.config import dictConfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr"
        },
        "syslog": {
            "class": "logging.handlers.SysLogHandler",
            "formatter": "default",
            "address": "/dev/log"
        }
    },
    "loggers": {
        "": {
            # Considering that systemd redirects stdout anyways to journald, we just need the stdout handler,
            # else we get dupe log messages in journald.
            "handlers": ["stdout", "syslog", "stderr"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
dictConfig(LOGGING)
log = getLogger()

