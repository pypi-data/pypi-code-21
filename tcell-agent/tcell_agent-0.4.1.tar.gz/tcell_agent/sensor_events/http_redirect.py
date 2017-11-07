# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils

from . import SensorEvent


def portless(host):
    if host:
        return host.split(':')[0]
    else:
        return host


class RedirectSensorEvent(SensorEvent):
    def __init__(self,
                 remote_addr,
                 method,
                 from_domain,
                 from_full_path,
                 status_code,
                 redirect_host,
                 user_id=None,
                 session_id=None,
                 route_id=None):
        super(RedirectSensorEvent, self).__init__("redirect")
        self["method"] = method
        self["remote_addr"] = remote_addr
        self["from_domain"] = portless(from_domain)
        self["status_code"] = status_code
        self["to"] = portless(redirect_host)

        if route_id:
            self["rid"] = route_id

        self.session_id = session_id
        self.raw_user_id = user_id
        self.raw_full_path = from_full_path

    def post_process(self):
        self["from"] = SanitizeUtils.strip_uri(self.raw_full_path)

        if self.raw_user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(self.raw_user_id))
            else:
                self["uid"] = str(self.raw_user_id)

        if self.session_id:
            self["sid"] = self.session_id
