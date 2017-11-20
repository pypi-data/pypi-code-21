""" AppOptics instrumentation for Tornado.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""
# useful methods for instrumenting Tornado
from __future__ import with_statement

import functools
import time

import tornado.web

from appoptics import util
from appoptics import async


# instrumentation functions for tornado.web.RequestHandler
def request_handler_start(self):
    """ runs from the main HTTP server thread (doesn't set/get Context)

        takes 'self' parameter, which is the current RequestHandler
        instance (which holds the current HTTPRequest in self.request)
    """
    start_time = int(time.time() * 1e6)

    # check for X-Trace header in HTTP request
    ctx, evt = util.Context.start_trace('tornado', xtr=self.request.headers.get("X-Trace"))

    if ctx.is_sampled() and evt.is_valid():
        if hasattr(self, '__class__') and hasattr(self.__class__, '__name__'):
            evt.add_info("Controller", self.__class__.__name__)
            evt.add_info("Action", self.request.method.lower())
        evt.add_info("URL", self.request.uri)
        evt.add_info("Method", self.request.method)
        evt.add_info("HTTP-Host", self.request.host)
        ctx.report(evt)
        ctx.set_as_default()

        # create & store finish event for reporting later
        self.request._appoptics_ctx = ctx
        self.request._appoptics_finish_ev = ctx.create_event('exit', 'tornado')
        # report the exit event ID in the response header
        self.set_header("X-Trace", self.request._appoptics_finish_ev.id())
    else:
        self.set_header("X-Trace", str(ctx))
    self.request._appoptics_span_start = start_time


RequestHandler_start = request_handler_start


def request_handler_finish(self):
    """ runs from the main HTTP server thread, or from write/flush() callback
        doesn't set/get Context; just checks if finish event was set by appoptics_start()
    """
    if hasattr(self, 'get_status'):  # recent Tornado
        status_code = self.get_status()
    elif hasattr(self, '_status_code'):  # older Tornado
        status_code = self._status_code
    else:
        status_code = 500

    ev = getattr(self.request, '_appoptics_finish_ev', None)
    ctx = getattr(self.request, '_appoptics_ctx', None)
    if ev and ctx and ctx.is_sampled():
        ev.add_info('Status', status_code)
        ev.add_edge(util.Context.get_default())
        ctx.report(ev)

        # clear the stored appoptics event/metadata from the request object
        self.request._appoptics_ctx = None
        self.request._appoptics_finish_ev = None

    util.Context.clear_default()

    start_time = getattr(self.request, '_appoptics_span_start', None)
    if start_time:
        stop_time = int(time.time() * 1e6)
        transaction_name = '{controller}.{action}'.format(
            controller=self.__class__.__name__,
            action=self.request.method.lower()
        )
        util.SwigSpan.createHttpSpan(
            transaction_name, None, stop_time - start_time, status_code,
            self.request.method, 499 < status_code < 600,
        )


RequestHandler_finish = request_handler_finish


# instrumentation for tornado.httpclient.AsyncHTTPClient
def AsyncHTTPClient_start(request):
    """ takes 'request' param, which is the outgoing HTTPRequest, not the request currently being handled """
    # this is called from AsyncHTTPClient.fetch(), which runs from the RequestHandler's context
    util.log("entry", "cURL", keys={'cURL_URL': request.url, 'Async': True})
    ctx = util.Context.get_default()
    if hasattr(request, 'headers'):
        if hasattr(request.headers, '__setitem__'):  # could be dict or tornado.httputil.HTTPHeaders
            request.headers['X-Trace'] = str(ctx)  # add X-Trace header to outgoing request

    if ctx.is_sampled():
        request._appoptics_ctx = ctx.copy()


def AsyncHTTPClient_finish(request, callback=None, headers=None):
    """
    fires exit event for Async HTTP requests.

    checks for wrapped metadata stored in user's callback function: if
    it exists, that metadata is used & updated when reporting the
    event, so that the callback will "happen after" the exit event.
    """
    if hasattr(callback, '_appoptics_ctx'):  # wrapped callback contains md
        ev = callback._appoptics_ctx.create_event('exit', 'cURL')  # adds edge to md
        if hasattr(request, '_appoptics_ctx'):  # add edge to entry event for this async HTTP call
            ev.add_edge(request._appoptics_ctx)
        mdobj = callback

    elif hasattr(request, '_appoptics_ctx'):  # callback contains no metadata, but request obj does
        ev = request._appoptics_ctx.create_event('exit', 'cURL')
        mdobj = request

    else:  # no metadata found
        return

    if headers and hasattr(headers, 'get') and headers.get('X-Trace', None):
        response_md = headers.get('X-Trace')
        ev.add_edge_str(response_md)  # add response X-Trace header

    mdobj._appoptics_ctx.report(ev)  # increments metadata in mdobj


# used for wrapping stack contexts in Tornado v1.2 stack_context.py
class AppOpticsContextWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        # get current context at wrap time (e.g. when preparing "done" callback for an async call)
        if util.Context.get_default().is_sampled():
            # store wrap-time context for use at call time
            self._appoptics_ctx = util.Context.get_default().copy()

    def __call__(self, *args, **kwargs):
        with async.AppOpticsContextManager(self):  # uses self._appoptics_ctx as context
            return self.wrapped.__call__(*args, **kwargs)


# replacement for _StackContextWrapper in Tornado v2.x stack_context.py
class _StackContextWrapper(functools.partial):
    def __init__(self, *args, **kwargs):
        if util.Context.get_default().is_sampled():
            self._appoptics_ctx = util.Context.get_default().copy()
        super(_StackContextWrapper, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with async.AppOpticsContextManager(self):
            return super(_StackContextWrapper, self).__call__(*args, **kwargs)


class AppOpticsBaseHandler(tornado.web.RequestHandler):
    """The base request handler to insert instrumentation code to the normal request 
    handling processes. All the request handlers of the application need to inherit 
    from this base class.
    """

    def prepare(self):
        """This function will be called by tornado.web.Application before the user 
        defined handler. If a handler inherits from this base handler, it should call
        this function in its own prepare() function."""
        super(AppOpticsBaseHandler, self).prepare()
        request_handler_start(self)

    def on_finish(self):
        """This function will be called by tornado.web.Application after the user defined
        handler. If a handler inherits from this base handler, it should call this function
        in its own prepare() function."""
        super(AppOpticsBaseHandler, self).on_finish()
        request_handler_finish(self)


util.report_layer_init('tornado')