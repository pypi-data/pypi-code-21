import logging
import os
import sys

log_level = int(os.environ.get('LOG_LEVEL', -1))

if log_level != -1:
    if log_level < 0 or log_level > 50 or log_level % 10 != 0:
        raise AttributeError('Invalid log level {}'.format(log_level))
    logging.basicConfig(level=log_level, stream=sys.stdout)
else:
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)


assert sys.version_info >= (3, 0), "Must be running Python Version 3.0+"