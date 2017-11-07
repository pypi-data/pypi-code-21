# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals


class SensorEvent(dict):
    def __init__(self, event_type, flush_right_away=False, ensure_delivery=False, send_event=True, queue_wait=False):
        self.queue_wait = queue_wait
        self.send_event = send_event
        self.flush_right_away = flush_right_away
        self.ensure_delivery = ensure_delivery
        self["event_type"] = event_type

    def get_debug_data(self):
        return "event id: {id} type: {event_type}".format(id=hex(id(self)),
                                                          event_type=self.get("event_type", "<unknown>"))

    def post_process(self):
        # implement here what the background thread should do
        # such as sanitization
        pass


from .app_config_settings import AppConfigSettings
from .http_redirect import RedirectSensorEvent
from .httptx import HttpTxSensorEvent
from .httptx import LoginFailureSensorEvent
from .httptx import LoginSuccessfulSensorEvent
from .httptx import FingerprintSensorEvent
from .server_agent_packages import ServerAgentPackagesEvent
from .server_agent_details import ServerAgentDetailsEvent
from .appsensor import AppSensorEvent
from .app_route import AppRouteSensorEvent
from .dlp import DlpEvent
from .login import LoginEvent
from .metrics import MetricsEvent
from .discovery import DiscoveryEvent
from .honeytoken import HoneytokenSensorEvent
