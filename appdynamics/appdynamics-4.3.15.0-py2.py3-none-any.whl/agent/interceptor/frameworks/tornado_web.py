# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import contextlib
import sys

from appdynamics.lib import LazyWsgiRequest
from appdynamics.agent.core.eum import inject_eum_metadata
from appdynamics.agent.models.transactions import ENTRY_TORNADO
from ..base import EntryPointInterceptor

try:
    import tornado.httputil
    import tornado.ioloop
    import tornado.stack_context
    import tornado.web
    import tornado.wsgi

    class TornadoFallbackHandlerInterceptor(EntryPointInterceptor):
        # When using FallbackHandler, the RequestHandler's finish method is
        # never called.  Wrap the custom fallback callable to end the bt here.
        def _initialize(self, initialize, handler, fallback):
            def _fallback(request):
                fallback(request)
                bt = self.bt
                if bt:
                    self.end_transaction(bt)
            initialize(handler, _fallback)

    class TornadoRequestHandlerInterceptor(EntryPointInterceptor):
        def __execute(self, _execute, handler, *args, **kwargs):
            bt = self.start_transaction(ENTRY_TORNADO,
                                        LazyWsgiRequest(tornado.wsgi.WSGIContainer.environ(handler.request)))

            if bt:
                @contextlib.contextmanager
                def current_bt_manager():
                    """Set and unset current_bt as tornado moves between execution contexts.

                    By wrapping the handler's execution with this we can ensure that whenever the
                    IOLoop is executing code for a particular BT, that BT is the 'current_bt'.
                    For more information see http://www.tornadoweb.org/en/stable/stack_context.html.

                    """
                    self.agent.set_current_bt(bt)
                    try:
                        yield
                    except:
                        # Currently can't figure out how to get here, so this code is untested.
                        bt.add_exception(*sys.exc_info())
                        raise
                    finally:
                        self.agent.unset_current_bt()

                with tornado.stack_context.StackContext(current_bt_manager):
                    result = _execute(handler, *args, **kwargs)
            else:
                result = _execute(handler, *args, **kwargs)

            return result

        def _finish(self, finish, handler, *args, **kwargs):
            result = finish(handler, *args, **kwargs)
            bt = self.bt
            if bt:
                with self.log_exceptions():
                    self.handle_http_status_code(bt, handler._status_code, handler._reason)
                    self.end_transaction(bt)
            return result

        def _flush(self, flush, handler, *args, **kwargs):
            with self.log_exceptions():
                if not handler._headers_written:
                    bt = self.bt
                    if bt:
                        headers = list(handler._headers.get_all())
                        inject_eum_metadata(self.agent.eum_config, bt, headers)
                        handler._headers = tornado.httputil.HTTPHeaders(headers)
            return flush(handler, *args, **kwargs)

        def __handle_request_exception(self, _handle_request_exception, handler, e, *args, **kwargs):
            with self.log_exceptions():
                bt = self.bt
                if bt and not (hasattr(tornado.web, 'Finish') and isinstance(e, tornado.web.Finish)):
                    bt.add_exception(*sys.exc_info())
            return _handle_request_exception(handler, e, *args, **kwargs)

    def intercept_tornado_web(agent, mod):
        TornadoRequestHandlerInterceptor(agent, mod.RequestHandler).attach(
            ['_execute', 'flush', '_handle_request_exception', 'finish'])
        TornadoFallbackHandlerInterceptor(agent, mod.FallbackHandler).attach('initialize')

except ImportError:
    def intercept_tornado_web(agent, mod):
        pass
