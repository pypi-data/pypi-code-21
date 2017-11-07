# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Django.

"""

from __future__ import unicode_literals
import sys

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from appdynamics.agent.interceptor.base import BaseInterceptor


class DjangoBaseHandlerInterceptor(BaseInterceptor):
    def _load_middleware(self, load_middleware, base_handler):
        load_middleware(base_handler)
        base_handler._exception_middleware.insert(0, AppDDjangoMiddleware(self).process_exception)

    def _handle_uncaught_exception(self, handle_uncaught_exception, base_handler, request, resolver, exc_info):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*exc_info)

        return handle_uncaught_exception(base_handler, request, resolver, exc_info)


class AppDDjangoMiddleware(object):
    def __init__(self, interceptor):
        self.interceptor = interceptor

    def process_exception(self, request, exception):
        with self.interceptor.log_exceptions():
            bt = self.interceptor.bt
            if bt:
                bt.add_exception(*sys.exc_info())


def intercept_django_wsgi_handler(agent, mod):
    WSGIInterceptor(agent, mod.WSGIHandler).attach('__call__')


def intercept_django_base_handler(agent, mod):
    DjangoBaseHandlerInterceptor(agent, mod.BaseHandler).attach(['load_middleware', 'handle_uncaught_exception'])
