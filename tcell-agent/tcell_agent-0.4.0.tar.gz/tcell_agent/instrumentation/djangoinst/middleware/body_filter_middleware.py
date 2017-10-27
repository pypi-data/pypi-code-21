# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import re

from django.http import HttpResponse

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.config import CONFIGURATION
from tcell_agent.instrumentation import safe_wrap_function


def add_tag(response):
    if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
        if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
            response_type = type(response.content)
            tag_policy = TCellAgent.get_policy(PolicyTypes.CSP)
            if tag_policy and tag_policy.js_agent_api_key:
                if CONFIGURATION.js_agent_api_base_url:
                    replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\" tcellbaseurl=\"" + CONFIGURATION.js_agent_api_base_url + "\"></script>"
                else:
                    replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\"></script>"

                if isinstance(response.content, str) is False:
                    replace = replace.encode("utf-8")

                try:
                    if response_type == str:
                        response.content = re.sub(b"<head>", replace, response.content.decode('utf8'))

                    else:
                        response.content = re.sub(b"<head>", replace, response.content)
                except UnicodeDecodeError:
                    pass


class BodyFilterMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return self.process_response(request, response)

    def process_response(self, request, response):
        safe_wrap_function("Insert Body Tag", add_tag, response)
        return response
