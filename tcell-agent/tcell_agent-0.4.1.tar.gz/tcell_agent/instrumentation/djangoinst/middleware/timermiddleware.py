# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.request_metrics.timing import start_timer, end_timer


class TimerMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    def process_request(self, request):
        safe_wrap_function("Start Request Timer", start_timer, request)

    def process_response(self, request, response):
        safe_wrap_function("Stop Request Timer", end_timer, request)
        return response
