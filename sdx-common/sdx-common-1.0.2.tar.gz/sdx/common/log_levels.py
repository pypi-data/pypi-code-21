import logging
import os


def set_level(logger=None, log_level=None):
    '''Set logging levels using logger names.

    :param logger: Name of the logger
    :type logger: String

    :param log_level: A string or integer corresponding to a Python logging level
    :type log_level: String

    :rtype: None

    '''
    log_level = logging.getLevelName(os.getenv('VERBOSITY', 'WARNING'))
    logging.getLogger(logger).setLevel(log_level)
