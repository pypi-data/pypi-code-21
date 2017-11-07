# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.config import CONFIGURATION
from tcell_agent.sensor_events import LoginEvent, HoneytokenSensorEvent
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware

from tcell_agent.instrumentation.utils import header_keys_from_request_env

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def _userLoggedIn(sender, user, request, **kwargs):  # pylint: disable=unused-argument
    def _set_loginfraud_success():
        if CONFIGURATION.should_instrument_django_auth():
            login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
            if login_policy is None or not login_policy.login_success_enabled:
                return
            request = GlobalRequestMiddleware.get_current_request()
            if request is not None:
                username = None
                try:
                    username = user.get_username()
                except:
                    pass
                if request:
                    try:
                        if request.method == "POST":
                            username = request.POST.get("user", username)
                            username = request.POST.get("email", username)
                            username = request.POST.get("email_address", username)
                            username = request.POST.get("username", username)
                        else:
                            username = request.GET.get("username", username)
                    except Exception as e:
                        LOGGER.error("Could not determine username for login success event: {e}".format(e=e))
                        LOGGER.debug(e, exc_info=True)
                LOGGER.debug("Login success event for {username}".format(username=username))
                event = LoginEvent().success(
                    user_id=username,
                    user_agent=request.META.get("HTTP_USER_AGENT", None),
                    referrer=request.META.get("HTTP_REFERER", None),
                    remote_addr=request._tcell_context.remote_addr,
                    header_keys=header_keys_from_request_env(request.META),
                    document_uri=request._tcell_context.fullpath,
                    session_id=request._tcell_context.session_id)
                TCellAgent.send(event)

    safe_wrap_function("LoginFraud login success", _set_loginfraud_success)


def _userLoginFailed(sender, credentials, **kwargs):  # pylint: disable=unused-argument
    def _set_loginfraud_failure():
        if CONFIGURATION.should_instrument_django_auth():
            login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
            if login_policy is None or not login_policy.login_failed_enabled:
                return
            request = GlobalRequestMiddleware.get_current_request()
            if request is not None:
                username = None
                if credentials:
                    username = credentials.get("username")
                LOGGER.debug("Login failed event for {username}".format(username=username))
                event = LoginEvent().failure(
                    user_id=username,
                    user_agent=request.META.get("HTTP_USER_AGENT", None),
                    referrer=request.META.get("HTTP_REFERER", None),
                    remote_addr=request._tcell_context.remote_addr,
                    header_keys=header_keys_from_request_env(request.META),
                    document_uri=request._tcell_context.fullpath,
                    session_id=request._tcell_context.session_id)
                TCellAgent.send(event)

    safe_wrap_function("LoginFraud login failure", _set_loginfraud_failure)


def _addUserLoginSignals():
    user_logged_in.connect(_userLoggedIn)
    user_login_failed.connect(_userLoginFailed)


def _addAuthIntercept():
    original_auth = ModelBackend.authenticate

    # Django 1.5 <= 1.10 method signature
    #     def authenticate(self, username=None, password=None, **kwargs):
    # Django 1.11 method signature
    #     def authenticate(self, request, username=None, password=None, **kwargs):
    def authenticate(self, *args, **kwargs):
        def _check_honeytoken_creds():
            if CONFIGURATION.should_instrument_django_auth():
                username = kwargs.get('username')
                password = kwargs.get('password')
                if username is None:
                    from django.contrib.auth import get_user_model
                    username = kwargs.get(get_user_model().USERNAME_FIELD)
                request = GlobalRequestMiddleware.get_current_request()
                if request:
                    honeytoken_policy = TCellAgent.get_policy(PolicyTypes.HONEYTOKEN)
                    if honeytoken_policy:
                        token_id = honeytoken_policy.get_id_for_credential(username, password)
                        if token_id:
                            event = HoneytokenSensorEvent(
                                token_id=token_id,
                                remote_addr=request._tcell_context.remote_addr
                            )
                            TCellAgent.send(event)

        safe_wrap_function("Honeytokens check", _check_honeytoken_creds)
        return original_auth(self, *args, **kwargs)

    ModelBackend.authenticate = authenticate


try:
    import django  # noqa pylint: disable=unused-import
    from django.contrib.auth.forms import AuthenticationForm  # noqa pylint: disable=unused-import

    if TCellAgent.tCell_agent:
        from django.contrib.auth.signals import user_logged_in, user_login_failed
        from django.db.backends.signals import connection_created  # noqa pylint: disable=unused-import

        safe_wrap_function("Adding user login signals", _addUserLoginSignals)
        from django.contrib.auth.backends import ModelBackend

        safe_wrap_function("Adding user honeytoken code", _addAuthIntercept)
except Exception as e:
    LOGGER.debug("Could not instrument django common-auth")
    LOGGER.debug(e, exc_info=True)
