# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

from __future__ import unicode_literals
import functools

from appdynamics.lang import get_args, urlparse
from . import HTTPConnectionInterceptor


try:
    import tornado.httpclient
    import tornado.stack_context

    class AsyncHTTPClientInterceptor(HTTPConnectionInterceptor):
        def start_exit_call(self, url):
            bt = self.bt
            if not bt:
                return None

            parsed_url = urlparse(url)
            port = parsed_url.port or ('443' if parsed_url.scheme == 'https' else '80')
            backend = self.get_backend(parsed_url.hostname, port, parsed_url.scheme, url)
            if not backend:
                return None

            return super(AsyncHTTPClientInterceptor, self).start_exit_call(bt, backend, operation=parsed_url.path)

        def end_exit_call(self, exit_call, future):
            super(AsyncHTTPClientInterceptor, self).end_exit_call(exit_call, exc_info=future.exc_info())

        def _fetch(self, fetch, client, request, callback=None, raise_error=True, **kwargs):
            exit_call = None
            with self.log_exceptions():
                is_request_object = isinstance(request, tornado.httpclient.HTTPRequest)
                url = request.url if is_request_object else request
                exit_call = self.start_exit_call(url)
                if exit_call:
                    correlation_header = self.make_correlation_header(exit_call)
                    if correlation_header:
                        headers = request.headers if is_request_object else kwargs.setdefault('headers', {})
                        headers[correlation_header[0]] = correlation_header[1]

            # The `raise_error` kwarg was added in tornado 4.1.  Passing it by name on versions
            # prior to this cause it to be included in the `**kwargs` parameter to `fetch`.  This
            # dict is passed directly to the `HTTPRequest` constructor, which does not have
            # `raise_error` in its signature and thus raises a TypeError.
            if 'raise_error' in get_args(fetch):
                future = fetch(client, request, callback=callback, raise_error=raise_error, **kwargs)
            else:
                future = fetch(client, request, callback=callback, **kwargs)
            future._callbacks.insert(0, functools.partial(tornado.stack_context.wrap(self.end_exit_call), exit_call))
            return future

    def intercept_tornado_httpclient(agent, mod):
        # these methods don't normally return anything, but to be able to test that
        # the 'empty' interceptor defined below works properly, return a value here.
        return AsyncHTTPClientInterceptor(agent, mod.AsyncHTTPClient).attach('fetch', wrapper_func=None)
except ImportError:
    def intercept_tornado_httpclient(agent, mod):
        pass
