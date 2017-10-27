# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils
from . import SensorEvent

"""
"event_type":"login",
"event_name":"login-success",
"user_agent":"Mozilla/5.0 ...",
"referrer":"http://localhost:3085/users/sign_in",
"remote_addr":"10.0.2.2",
"header_keys":["VERSION","HOST","CONNECTION","CACHE_CONTROL","COOKIE"],
"user_id":"1",
"document_uri":"/users/sign_in",
"session":"e9e80cd52ad521ddb9090ac9ac",
"user_valid": true
"""


class LoginEvent(SensorEvent):
    def __init__(self):
        super(LoginEvent, self).__init__("login")
        self.raw_referrer = None
        self.raw_uri = None

    def success(self, *args, **kwargs):
        self["event_name"] = "login-success"
        return self._add_details(*args, **kwargs)

    def failure(self, *args, **kwargs):
        self["event_name"] = "login-failure"
        return self._add_details(*args, **kwargs)

    def _add_details(self, user_id, user_agent, referrer, remote_addr, header_keys, document_uri, session_id=None):
        self.raw_referrer = referrer
        self.raw_uri = document_uri

        if user_agent:
            self["user_agent"] = user_agent
        if remote_addr:
            self["remote_addr"] = remote_addr
        if header_keys:
            self["header_keys"] = header_keys

        if session_id:
            self["session"] = session_id

        if user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["user_id"] = SanitizeUtils.hmac(str(user_id))
            else:
                self["user_id"] = str(user_id)

        return self

    def post_process(self):
        if self.raw_uri is not None:
            self["document_uri"] = SanitizeUtils.strip_uri(self.raw_uri)

        if self.raw_referrer is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["referrer"] = SanitizeUtils.hmac(SanitizeUtils.strip_uri(self.raw_referrer))
            else:
                self["referrer"] = SanitizeUtils.strip_uri(self.raw_referrer)
