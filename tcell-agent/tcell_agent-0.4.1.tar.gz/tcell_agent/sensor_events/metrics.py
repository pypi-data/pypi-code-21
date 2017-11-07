# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from . import SensorEvent


class MetricsEvent(SensorEvent):
    def __init__(self):
        super(MetricsEvent, self).__init__("metrics")

    def set_rct(self, route_count_table):
        self["rct"] = route_count_table

    def set_session(self, session_info):
        if session_info:
            self["sessions"] = session_info
