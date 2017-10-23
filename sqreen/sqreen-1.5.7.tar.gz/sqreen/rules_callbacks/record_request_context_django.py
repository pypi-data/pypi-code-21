# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..frameworks.django_framework import DjangoRequest
from ..runtime_infos import runtime
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextDjango(RecordRequestContext):

    def pre(self, original, request, view_func, view_args, view_kwargs):
        self._store_request(DjangoRequest(request, view_func, view_args, view_kwargs))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        """ Post is always called in a Django Middleware, don't clean the
        request right now as it may be needed in a post callback
        """
        pass
