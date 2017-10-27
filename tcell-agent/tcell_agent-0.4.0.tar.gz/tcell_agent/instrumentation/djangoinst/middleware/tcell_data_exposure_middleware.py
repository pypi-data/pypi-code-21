# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging
import re

from tcell_agent.agent import TCellAgent, PolicyTypes

from tcell_agent.instrumentation import safe_wrap_function

logger = logging.getLogger('tcell_agent').getChild(__name__)
django_header_regex = re.compile('^HTTP_')


def parameter_list(dataloss_policy, request, query_dict, route_id):
    for parameter in query_dict:
        parameter_lower = parameter.lower()
        actions = dataloss_policy.get_actions_for_form_parameter(parameter_lower, route_id)
        if actions is None:
            continue
        parameter_values = query_dict.getlist(parameter, [])
        for action in actions:
            for parameter_value in parameter_values:
                request._tcell_context.add_response_parameter_filter(parameter_value, action, parameter)


def form_dataex(dataloss_policy, request):
    route_id = request._tcell_context.route_id

    parameter_list(dataloss_policy, request, request.GET, route_id)
    parameter_list(dataloss_policy, request, request.POST, route_id)


def cookie_dataex(dataloss_policy, request):
    route_id = request._tcell_context.route_id
    for cookie in request.COOKIES:
        actions = dataloss_policy.get_actions_for_cookie(cookie, route_id)
        if actions is None:
            continue
        cookie_value = request.COOKIES.get(cookie)
        for action in actions:
            request._tcell_context.add_response_cookie_filter(cookie_value, action, cookie)


def header_dataex(dataloss_policy, request):
    route_id = request._tcell_context.route_id
    headers = dict((django_header_regex.sub('', header), value) for (header, value)
                   in request.META.items() if header.startswith('HTTP_'))
    for header in headers:
        actions = dataloss_policy.get_actions_for_header(header.lower(), route_id)
        if actions is None:
            continue
        header_value = headers.get(header)
        for action in actions:
            request._tcell_context.add_header_filter(header_value, action, header)


def dataex_middleware(request):
    dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
    if dataloss_policy and dataloss_policy.enabled:
        safe_wrap_function("Data-Exposure for Request Forms", form_dataex, dataloss_policy, request)
        safe_wrap_function("Data-Exposure for Request Cookies", cookie_dataex, dataloss_policy, request)
        safe_wrap_function("Data-Exposure for Request Headers", header_dataex, dataloss_policy, request)


class TCellDataExposureMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        return self.get_response(request)

    def process_request(self, request):
        safe_wrap_function("Data-Exposure Middleware", dataex_middleware, request)
