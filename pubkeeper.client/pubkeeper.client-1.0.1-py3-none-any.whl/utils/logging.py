import logging


class _Logging(object):
    """ Provides logging functionality for client and its brews
    """

    def __init__(self):
        self._prefix = None

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    def get_logger(self, logger_name):
        if self.prefix:
            logger_name = "{}.{}".format(self.prefix, logger_name)
        return logging.getLogger(logger_name)


Logging = _Logging()


def get_logger(logger_name):
    return Logging.get_logger(logger_name)
