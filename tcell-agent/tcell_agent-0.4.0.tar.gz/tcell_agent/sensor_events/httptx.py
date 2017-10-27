# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import json
import re
import logging

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils
from . import SensorEvent

logger = logging.getLogger('tcell_agent').getChild(__name__)


class HttpTxSensorEvent(SensorEvent):
    def __init__(self, request, response, event_name=None):
        super(HttpTxSensorEvent, self).__init__("http_tx")
        if event_name is not None:
            self["event_name"] = event_name
        self.raw_request = request
        self.raw_response = response

    def post_process(self):
        self["request"] = {}
        self["response"] = {}
        try:
            from django.http.request import HttpRequest
            from django.http.response import HttpResponse
            if isinstance(self.raw_request, HttpRequest):
                self["request"] = HttpRequestInfo.from_django_request(self.raw_request)
            if isinstance(self.raw_response, HttpResponse):
                self["response"] = HttpResponseInfo.from_django_response(self.raw_response)
        except Exception as e:
            # Not Django-request-response
            logger.debug(e)
        self["request"] = SanitizeUtils.sanitize_request_info(self["request"])
        self["response"] = SanitizeUtils.sanitize_response_info(self["response"])


class LoginFailureSensorEvent(HttpTxSensorEvent):
    def __init__(self, request, response):
        super(LoginFailureSensorEvent, self).__init__(request, response)
        self["event_name"] = "login_failure"


class LoginSuccessfulSensorEvent(HttpTxSensorEvent):
    def __init__(self, request, response):
        super(LoginSuccessfulSensorEvent, self).__init__(request, response)
        self["event_name"] = "login_success"


class FingerprintSensorEvent(SensorEvent):
    def __init__(self, request, hmac_session_id, user_id=None):
        super(FingerprintSensorEvent, self).__init__("fingerprint")
        self.hmac_session_id = hmac_session_id
        self.raw_request = request
        self.user_id = user_id

    def post_process(self):
        request = None
        if self.raw_request._tcell_sensors_httpx.get("uuid"):
            self["tid"] = self.raw_request._tcell_sensors_httpx.get("uuid")
        try:
            from django.http.request import HttpRequest
            if isinstance(self.raw_request, HttpRequest):
                request = HttpRequestInfo.from_django_request(self.raw_request)
        except Exception as e:
            # Not Django-request-response
            logger.debug(e)
        if request:
            # we have a valid request/response pair
            ua = request.get("headers", {}).get("User_agent")
            if ua:
                ua = "".join(ua)
            ip = request.get("remote_host")
            sid = self.hmac_session_id
            self["ua"] = ua
            self["ip"] = ip
            self["sid"] = sid

            if self.user_id is not None:
                if CONFIGURATION.hipaa_safe_mode:
                    self["uid"] = SanitizeUtils.hmac(str(self.user_id))
                else:
                    self["uid"] = str(self.user_id)


class HttpMessageInfo(dict):
    def __init__(self):
        self["headers"] = {}


class HttpRequestInfo(HttpMessageInfo):
    uri = None
    method = None
    remote_host = None
    post_data = None

    def __str__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_django_request(cls, request):
        request_info = HttpRequestInfo()
        request_info["uri"] = request.build_absolute_uri()
        request_info["remote_host"] = request.META.get("REMOTE_ADDR")
        request_info["method"] = request.method
        request_info["post_data"] = request.body
        regex = re.compile('^HTTP_')
        raw_headers = dict((regex.sub('', header), value) for (header, value)
                           in request.META.items() if header.startswith('HTTP_'))
        headers = {}
        for header_name, header_value in raw_headers.items():
            header_name = header_name.capitalize()
            if headers.get(header_name):
                headers[header_name].append(header_value)
            else:
                headers[header_name] = [header_value]
        request_info["headers"] = headers
        return request_info


class HttpResponseInfo(HttpMessageInfo):
    def __str__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_django_response(cls, response):
        response_info = HttpResponseInfo()
        response_info["status"] = response.status_code
        response_info["content_type"] = response.get("content-type")
        headers = {}
        for header_name, header_value in response.items():
            if headers.get(header_name):
                headers[header_name].append(header_value)
            else:
                headers[header_name] = [header_value]
        response_info["headers"] = headers
        return response_info
