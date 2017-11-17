import contextlib
import logging
import logging.config
import os
import time

FORMAT = '[%(asctime)s] %(levelname)s pid:%(process)d t:%(thread)d %(name)s:%(lineno)d %(message)s'
LOGGER = logging.getLogger(__name__)

def level_for_environment():
    env = os.environ.get('LOG_LEVEL')
    return {
        'debug'     : logging.DEBUG,
        'info'      : logging.INFO,
        'warning'   : logging.WARNING,
        'error'     : logging.ERROR,
    }.get(env, logging.INFO)

def setup_logging(level=None):
    level = level if level else level_for_environment()
    configuration = {
        'version'   : 1,
        'disable_existing_loggers'  : False,
        'formatters'                : {
            'standard'              : {
                'format'            : FORMAT,
                'dateformat'        : '%d/%b/%Y:%H:%M:%S %z',
            },
        },
        'handlers'                  : {
            'console'               : {
                'level'             : level,
                'class'             : 'logging.StreamHandler',
                'formatter'         : 'standard',
            },
        },
        'loggers'                   : {
            ''                      : {
                'handlers'          : ['console'],
                'level'             : level,
                'propogate'         : True,
            },
        },
    }
    logging.config.dictConfig(configuration)

@contextlib.contextmanager
def warning_timer(seconds, message, start=None):
    start = start or time.time()
    yield
    end = time.time()
    if (end - start) > seconds:
        LOGGER.warning("Took %s seconds doing %s", end - start, message)
