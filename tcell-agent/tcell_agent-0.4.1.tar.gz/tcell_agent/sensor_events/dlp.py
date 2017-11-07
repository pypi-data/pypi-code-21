# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils
from . import SensorEvent


class DlpEvent(SensorEvent):
    FOUND_IN_BODY = "body"
    FOUND_IN_LOG = "log"
    FOUND_IN_CONSOLE = "console"

    FRAMEWORK_VARIABLE_SESSION_ID = "session_id"

    REQUEST_CONTEXT_FORM = "form"
    REQUEST_CONTEXT_COOKIE = "cookie"
    REQUEST_CONTEXT_HEADER = "header"

    def __init__(self,
                 route_id,
                 raw_uri,
                 found_in,
                 action_id=None,
                 user_id=None,
                 hmac_session_id=None):
        super(DlpEvent, self).__init__("dlp")
        if route_id:
            self["rid"] = route_id
        self.raw_uri = raw_uri
        self["found_in"] = found_in
        if action_id:
            self["rule"] = action_id
        if hmac_session_id:
            self["sid"] = hmac_session_id

        if user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(user_id))
            else:
                self["uid"] = str(user_id)

    def for_database(self, database, schema, table, field):
        self["type"] = "db"
        self["db"] = database
        self["schema"] = schema
        self["table"] = table
        self["field"] = field
        return self

    def for_framework(self, framwork_variable):
        self["type"] = "framework"
        self["variable"] = framwork_variable
        return self

    def for_request(self, context, variable):
        self["type"] = "request"
        self["context"] = context
        self["variable"] = variable
        return self

    def post_process(self):
        if self.raw_uri:
            self["uri"] = SanitizeUtils.strip_uri(self.raw_uri)
