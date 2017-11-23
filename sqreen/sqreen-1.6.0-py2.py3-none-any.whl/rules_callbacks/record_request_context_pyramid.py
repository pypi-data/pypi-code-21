# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..frameworks.pyramid_framework import PyramidRequest
from ..runtime_infos import runtime
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextPyramid(RecordRequestContext):

    def pre(self, original, request):
        self._store_request(PyramidRequest(request))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        runtime.clear_request()
