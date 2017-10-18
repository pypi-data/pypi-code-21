# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Record the current request in flask application
"""
from logging import getLogger

from ..frameworks.flask_framework import FlaskRequest
from ..runtime_infos import runtime
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextFlask(RecordRequestContext):

    def pre(self, original, *args, **kwargs):
        from flask import request
        self._store_request(FlaskRequest(request))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        """ Post is always called in a Flask Middleware, don't clean the
        request right now as it may be needed in a post callback
        """
        pass
