# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import uuid

import threading
import logging

from django import get_version
from django.http import HttpResponse

from django.conf import settings
from django.core.urlresolvers import get_resolver, set_urlconf

import tcell_agent
from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.djangoinst.routes import get_route_table
from tcell_agent.instrumentation.djangoinst.settings import send_django_setting_events
from tcell_agent.sensor_events import ServerAgentDetailsEvent
from tcell_agent.sensor_events.httptx import FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def assign_route_id(request):
    urlconf = settings.ROOT_URLCONF
    set_urlconf(urlconf)
    resolver = get_resolver(urlconf)
    try:
        resolver_match = resolver.resolve(request.path_info)
    except:
        return
    if resolver_match:
        route_table = get_route_table()
        request._tcell_context.route_id = route_table.get(resolver_match.func, {}).get("route_id")


def initialize_request(request):
    request._tcell_context.transaction_id = str(uuid.uuid4())
    request._tcell_context.user_agent = request.META.get("HTTP_USER_AGENT")
    raw_ip_address = better_ip_address(request.META)
    request._tcell_context.set_remote_addr(raw_ip_address)
    request._tcell_context.method = request.method


def set_fullpath(request):
    request._tcell_context.fullpath = request.get_full_path()


AGENT_STARTED_LOCK = threading.Lock()


def ensure_agent_started():
    AGENT_STARTED_LOCK.acquire()
    if tcell_agent.instrumentation.djangoinst.app._started:
        AGENT_STARTED_LOCK.release()
        return

    else:
        tcell_agent.instrumentation.djangoinst.app._started = True
        AGENT_STARTED_LOCK.release()

    LOGGER.info("Starting agent")

    TCellAgent.get_agent().ensure_polling_thread_running()

    sade = ServerAgentDetailsEvent(framework="Django", framework_version=get_version())
    TCellAgent.send(sade)
    send_django_setting_events()

    if settings.DEFAULT_CHARSET:
        tcell_agent.instrumentation.djangoinst.app._default_charset = settings.DEFAULT_CHARSET


class GlobalRequestMiddleware(object):
    _threadmap = {}

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    @classmethod
    def get_current_request(cls):
        try:
            return cls._threadmap[threading.current_thread().ident]
        except Exception:
            pass

    def process_request(self, request):
        if not tcell_agent.instrumentation.djangoinst.app._started:
            ensure_agent_started()

        request._tcell_signals = {}

        request._tcell_context = TCellInstrumentationContext()

        safe_wrap_function("Setting Transaction Id", initialize_request, request)
        safe_wrap_function("Setting Request FullPath", set_fullpath, request)
        safe_wrap_function("Assiging route ID to request (global)", assign_route_id, request)

        self._threadmap[threading.current_thread().ident] = request

    def process_exception(self, request, exception):
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass

    def process_response(self, request, response):
        safe_wrap_function("Check Location Header", self.checkLocationRedirect, request, response)
        safe_wrap_function("Insert CSP Headers", self.addCSP, request, response)
        safe_wrap_function("Insert Clickjacking Headers", self.addClickjacking, request, response)
        safe_wrap_function("Insert Secure Headers", self.addSecureHeaders, request, response)
        safe_wrap_function("Running Filters", self.run_filters, request, response)
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass
        return response

    def run_filters(self, request, response):
        if isinstance(response, HttpResponse):
            response.content = request._tcell_context.filter_body(response.content)

    def addSecureHeaders(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS):
            secure_headers = TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS).headers()
            if secure_headers:
                for secure_header in secure_headers:
                    response[secure_header[0]] = secure_header[1]

    def addCSP(self, request, response):
        if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
            if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
                if TCellAgent.get_policy(PolicyTypes.CSP):
                    csp_headers = TCellAgent.get_policy(PolicyTypes.CSP).headers(
                        request._tcell_context.transaction_id,
                        request._tcell_context.route_id,
                        request._tcell_context.session_id,
                        request._tcell_context.user_id,
                        request.path_info)
                    if csp_headers:
                        for csp_header in csp_headers:
                            header_value = csp_header[1]
                            response[csp_header[0]] = header_value

    def addClickjacking(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.CLICKJACKING):
            csp_headers = TCellAgent.get_policy(PolicyTypes.CLICKJACKING).headers(
                request._tcell_context.transaction_id,
                request._tcell_context.route_id,
                request._tcell_context.session_id,
                request._tcell_context.user_id)
            if csp_headers:
                for csp_header in csp_headers:
                    header_value = csp_header[1]
                    if response.has_header(csp_header[0]):
                        response[csp_header[0]] = response[csp_header[0]] + ", " + header_value
                    else:
                        response[csp_header[0]] = header_value

    def checkLocationRedirect(self, request, response):
        redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

        if redirect_policy and response.get("location"):
            response["location"] = redirect_policy.process_location(
                request._tcell_context.remote_addr,
                request.method,
                request.get_host(),
                request.get_full_path(),
                response.status_code,
                response.get("location"),
                user_id=request._tcell_context.user_id,
                session_id=request._tcell_context.session_id,
                route_id=request._tcell_context.route_id)

    def handleFingerprint(self, request, response):
        # if TCellAgent.tCell_agent.httptx_policy.fingerprint.get("enabled") and \
        event = FingerprintSensorEvent(request, request._tcell_context.session_id)
        TCellAgent.send(event)

    def handleLoginSuccessfulSignal(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.HTTP_TX).auth_framework.get("enabled") and \
                request._tcell_sensors_httpx.get("login_attempt"):
            event = LoginSuccessfulSensorEvent(request, response)
            TCellAgent.send(event)

    def handleLoginFailureSignal(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.HTTP_TX).auth_framework.get("enabled") and \
                request._tcell_sensors_httpx.get("login_attempt"):
            event = LoginFailureSensorEvent(request, response)
            TCellAgent.send(event)
            # elif TCellAgent.tCell_agent.httptx_policy.firehose.get("enabled"):
            #    content_type = response.get("content-type")
            #    if (content_type and content_type.lower().startswith("text/html")):
            #        LOGGER.debug("firehose event")
            #        event = HttpTxSensorEvent(request, response)
            #        TCellAgent.send(event)
