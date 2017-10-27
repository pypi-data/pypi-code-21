# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import json

from tcell_agent.agent import TCellAgent
from tcell_agent.sensor_events import AppConfigSettings
from .. import safe_wrap_function


def send_django_setting_events():
    from django.conf import settings

    safe_wrap_function(
        "Settings: Check cookie sesion length",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_COOKIE_HTTPONLY",
            settings.SESSION_COOKIE_HTTPONLY
        ))
    )
    safe_wrap_function(
        "Settings: Check cookie sesion secure",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_COOKIE_SECURE",
            settings.SESSION_COOKIE_SECURE
        ))
    )
    safe_wrap_function(
        "Settings: Check cookie sesion expiration",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_EXPIRE_AT_BROWSER_CLOSE",
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
        ))
    )
    safe_wrap_function(
        "Settings: Debug turned off",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "DEBUG",
            settings.DEBUG
        ))
    )
    safe_wrap_function(
        "Settings: Allowed Host Length",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "ALLOWED_HOSTS_LEN",
            len(settings.ALLOWED_HOSTS)
        ))
    )
    safe_wrap_function(
        "Settings: List of password hashes",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Auth",
            "PASSWORD_HASHERS",
            json.dumps(settings.PASSWORD_HASHERS)
        ))
    )
    safe_wrap_function(
        "Settings: Password reset timeout in days",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Auth",
            "PASSWORD_RESET_TIMEOUT_DAYS",
            settings.PASSWORD_RESET_TIMEOUT_DAYS
        ))
    )
