# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Record request context
"""

from logging import getLogger

from ..frameworks.wsgi import WSGIRequest
from ..rules import RuleCallback
from ..runtime_infos import runtime

LOGGER = getLogger(__name__)


class RecordRequestContext(RuleCallback):

    def pre(self, *args, **kwargs):
        self._store_request(WSGIRequest(args[-2]))

    def _store_request(self, request):
        runtime.store_request(request)
        if self.runner is None or not self.runner.whitelisted_metric:
            return
        whitelist_match = runtime.get_whitelist_match(self.runner.settings)
        if whitelist_match is not None:
            self.record_observation('whitelisted', whitelist_match, 1)

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        runtime.clear_request()

    @property
    def whitelisted(self):
        return False
