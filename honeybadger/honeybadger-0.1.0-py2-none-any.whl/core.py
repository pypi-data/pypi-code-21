from contextlib import contextmanager
import threading
import sys
import logging
import copy

import honeybadger.connection as connection
import honeybadger.fake_connection as fake_connection
from .payload import create_payload
from .config import Configuration

logging.getLogger('honeybadger').addHandler(logging.NullHandler())

class Honeybadger(object):
    def __init__(self):
        self.config = Configuration()
        self.thread_local = threading.local()
        self.thread_local.request = None
        self.thread_local.context = {}

    def _send_notice(self, exception, exc_traceback=None, context={}):
        payload = create_payload(exception, exc_traceback, request=self.thread_local.request, config=self.config, context=context)
        if self.config.is_dev() and not self.config.force_report_data:
            fake_connection.send_notice(self.config, payload)
        else:
            connection.send_notice(self.config, payload)

    def begin_request(self, request):
        self.thread_local.request = request
        self.thread_local.context = getattr(self.thread_local, 'context', {})

    def wrap_excepthook(self, func):
        self.existing_except_hook = func
        sys.excepthook = self.exception_hook

    def exception_hook(self, type, value, exc_traceback):
        self._send_notice(value, exc_traceback, context=self.thread_local.context)
        self.existing_except_hook(type, value, exc_traceback)

    def notify(self, exception=None, error_class=None, error_message=None, context={}):
        if exception is None:
            exception = {
                'error_class': error_class,
                'error_message': error_message
            }

        merged_context = self.thread_local.context
        merged_context.update(context)

        self._send_notice(exception, context=merged_context)

    def configure(self, **kwargs):
        self.config.set_config_from_dict(kwargs)

    def set_context(self, **kwargs):
        self.thread_local.context = getattr(self.thread_local, 'context', {})
        self.thread_local.context.update(kwargs)

    def reset_context(self):
        self.thread_local.context = {}

    @contextmanager
    def context(self, **kwargs):
        original_context = copy.copy(self.thread_local.context)
        self.thread_local.context.update(kwargs)
        try:
            yield
        except:
            raise
        else:
            self.thread_local.context = original_context
