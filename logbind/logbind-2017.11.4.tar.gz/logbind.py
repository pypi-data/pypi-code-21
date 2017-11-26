"""
logbind
=======

Much, much easier interface for ``LoggerAdapter``: bind new fields to
loggers.

"""

import logging


__version__ = '2017.11.4'


def bind(logger, **kwargs):
    # type: (logging.Logger, ...) -> logging.LoggerAdapter

    class Adapter(logging.LoggerAdapter):
        def __init__(self, logger, extra):
            try:
                # Reuse "extra" from the given logger, if present.
                extra.update(logger.extra)
            except AttributeError:
                pass

            super(Adapter, self).__init__(logger, extra)
            if not hasattr(self, '_log'):
                self._log = logger._log

    return Adapter(logger, kwargs)
