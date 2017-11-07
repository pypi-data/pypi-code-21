# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils

from . import SensorEvent


def build_from_native_lib_event(event):
    return AppSensorEvent(
        detection_point=event.get("dp"),
        parameter=event.get("param"),
        location=event.get("uri"),
        remote_address=event.get("remote_addr"),
        route_id=event.get("rid"),
        meta=event.get("meta"),
        method=event.get("m"),
        payload=event.get("payload"),
        user_id=event.get("uid"),
        session_id=event.get("sid"),
        pattern=event.get("pattern"),
        full_uri=event.get("full_uri")
    )


def build_from_meta(appsensor_meta,
                    detection_point,
                    parameter,
                    meta,
                    payload=None,
                    collect_full_uri=False):
    full_uri = None
    if collect_full_uri:
        full_uri = appsensor_meta.location

    reduced_payload = payload
    if reduced_payload:
        reduced_payload = reduced_payload[:150]

    return AppSensorEvent(
        detection_point=detection_point,
        parameter=parameter,
        location=appsensor_meta.location,
        remote_address=appsensor_meta.remote_address,
        route_id=appsensor_meta.route_id,
        meta=meta,
        method=appsensor_meta.method,
        payload=reduced_payload,
        user_id=appsensor_meta.user_id,
        session_id=appsensor_meta.session_id,
        pattern=None,
        full_uri=full_uri
    )


class AppSensorEvent(SensorEvent):
    def __init__(self,
                 detection_point,
                 parameter,
                 location,
                 remote_address,
                 route_id,
                 meta,
                 method,
                 session_id=None,
                 user_id=None,
                 count=None,
                 payload=None,
                 pattern=None,
                 full_uri=None):
        super(AppSensorEvent, self).__init__("as")
        self["dp"] = detection_point

        if parameter is not None:
            self["param"] = parameter
        if method is not None:
            self["m"] = method
        if meta is not None:
            self["meta"] = meta
        if route_id is not None:
            self["rid"] = str(route_id)
        if session_id is not None:
            self["sid"] = session_id
        if count is not None:
            self["count"] = count
        if pattern is not None:
            self["pattern"] = pattern
        if full_uri is not None:
            self["full_uri"] = full_uri
        if location is not None:
            self["uri"] = location

        if (not CONFIGURATION.hipaa_safe_mode) and CONFIGURATION.allow_payloads and (payload is not None):
            self["payload"] = payload

        if remote_address is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["remote_addr"] = "hmac:{ip}".format(ip=remote_address)
            else:
                self["remote_addr"] = remote_address

        if user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(user_id))
            else:
                self["uid"] = str(user_id)
