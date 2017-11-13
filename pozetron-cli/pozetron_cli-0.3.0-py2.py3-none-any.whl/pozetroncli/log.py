import logging.config
import os
import os.path as op

from .conf import get_logs_dir


def configure_logging(verbose=False):
    logs_dir = get_logs_dir()
    try:
        os.makedirs(logs_dir)
    except OSError:
        pass
    config = {
        'version': 1,
        'formatters': {
            'brief': {
                'format': '%(message)s',
            },
            'verbose': {
                'format': '%(asctime)s %(levelname)-5s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG' if verbose else 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose' if verbose else 'brief',
                'stream': 'ext://sys.stderr'
            },
            'file': {
                'level': 'DEBUG' if verbose else 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': op.join(logs_dir, 'poze.log'),
                'maxBytes': 0x10000,
                'backupCount': 3
            }
        },
        'loggers': {
            'brief': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            },
            'verbose': {
                'level': 'DEBUG',
                'handlers': ['file'] + (['console'] if verbose else [])
            }
        },
        'disable_existing_loggers': True
    }
    logging.config.dictConfig(config)
