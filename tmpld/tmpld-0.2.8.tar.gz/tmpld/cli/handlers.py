"""
tmpld.cli.handlers
~~~~~~~~~~~~~~

Cement handlers for tmpld cement app.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import sys

from cement.core.output import CementOutputHandler
from cement.ext.ext_logging import LoggingLogHandler


class StandardOutputHandler(CementOutputHandler):
    class Meta:
        label = 'stdout'

    def render(self, msg, *args, **kwargs):
        print(msg)


class StandardErrorHandler(CementOutputHandler):
    class Meta:
        label = 'stderr'

    def render(self, msg, *args, **kwargs):
        print(msg, file=sys.stderr)


class KubeWaitLogHandler(LoggingLogHandler):
    class Meta(LoggingLogHandler.Meta):
        label = 'kwlogging'
        console_format = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        debug_format = console_format

    def debug(self, msg, *args, **kwargs):
        self.backend.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.backend.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.backend.warning(msg, *args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        self.backend.error(msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self.backend.fatal(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.backend.exception(msg, *args, **kwargs)
