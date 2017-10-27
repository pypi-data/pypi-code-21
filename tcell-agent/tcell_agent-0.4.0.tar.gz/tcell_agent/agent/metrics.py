# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals

import threading
import logging

from collections import defaultdict

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

metricsLock = threading.Lock()
requestCountLock = threading.Lock()


class Counter(object):
    def __init__(self):
        self.counter = 0

    def add_object(self):
        self.counter += 1

    def reset(self):
        self.counter = 0


class RouteCountMetric(dict):
    def __init__(self, *args, **kwargs):
        super(RouteCountMetric, self).__init__(*args, **kwargs)
        self["c"] = 0
        self["mx"] = 0
        self["mn"] = 0
        self["t"] = 0


class UserSessionTrackMetric(dict):
    def __init__(self, object_counter, user_id):
        dict.__init__(self)
        self.object_counter = object_counter
        self._track = defaultdict(list)
        self["uid"] = str(user_id)
        self["track"] = None

    def add_user_agent_ip_combo(self, user_agent, ip):
        if user_agent and len(user_agent) > 256:
            user_agent = user_agent[:256]

        if ip not in self._track[user_agent]:
            self._track[user_agent].append(ip)
            self["track"] = [[ua, self._track[ua]] for ua in self._track]
            self.object_counter.add_object()


class UserSessionMetric(list):
    def __init__(self, object_counter):
        self._tracks = dict()
        self.object_counter = object_counter

    def for_user_id(self, user_id):
        if user_id not in self._tracks:
            self.object_counter.add_object()
            self._tracks[user_id] = UserSessionTrackMetric(self.object_counter, user_id)
            self.append(self._tracks[user_id])
        return self._tracks[user_id]


class SessionsMetric(dict):
    def __init__(self, object_counter, *arg, **kw):
        dict.__init__(self, *arg, **kw)
        self.object_counter = object_counter

    def for_session(self, session_id):
        if session_id not in self:
            self[session_id] = UserSessionMetric(self.object_counter)
            self.object_counter.add_object()
        return self[session_id]


class AgentMetrics(object):
    def __init__(self):
        self.object_counter = Counter()
        self._session_metrics = SessionsMetric(self.object_counter)
        self._flush_signal = False

        self._route_count_table = defaultdict(RouteCountMetric)
        self._route_count_table_flush_signal = False

    def get_and_reset_sesssion_metric(self):
        session_metrics = None
        metricsLock.acquire()
        try:
            session_metrics = self._session_metrics
            self._session_metrics = SessionsMetric(self.object_counter)
            self._flush_signal = False
            self.object_counter.reset()
        finally:
            metricsLock.release()
        return session_metrics

    def get_object_count(self):
        return self.object_counter.counter

    def should_send_flush_event(self):
        metricsLock.acquire()
        try:
            if self.object_counter.counter >= 250 and not self._flush_signal:
                return True
        finally:
            metricsLock.release()
        return False

    def add_session_track_metric(self, session_id, user_id, user_agent, remote_addr):
        metricsLock.acquire()
        try:
            if self.object_counter.counter >= 250:
                return
            if CONFIGURATION.hipaa_safe_mode:
                user_id = SanitizeUtils.hmac(str(user_id))
            self._session_metrics.for_session(session_id).for_user_id(user_id).add_user_agent_ip_combo(user_agent,
                                                                                                       remote_addr)
        except Exception as e:
            LOGGER.error("Updating metrics error: {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)
        finally:
            metricsLock.release()

    def should_send_flush_event_for_route_count_table(self):
        requestCountLock.acquire()
        try:
            if len(self._route_count_table) >= 150 and not self._route_count_table_flush_signal:
                self._route_count_table_flush_signal = True
                return True
        finally:
            requestCountLock.release()
        return False

    def get_and_reset_route_count_table(self):
        route_count_table = None
        requestCountLock.acquire()
        try:
            route_count_table = dict(self._route_count_table)
            self._route_count_table = defaultdict(RouteCountMetric)
            self._route_count_table_flush_signal = False
        finally:
            requestCountLock.release()
        return route_count_table

    def add_route_count(self, route_id, request_time):
        requestCountLock.acquire()
        try:
            if len(self._route_count_table) >= 150:
                return
            self._route_count_table[route_id]["c"] += 1
            self._route_count_table[route_id]["mx"] = max(self._route_count_table[route_id]["mx"], request_time)
            if self._route_count_table[route_id]["mn"] == 0:
                self._route_count_table[route_id]["mn"] = request_time
            else:
                self._route_count_table[route_id]["mn"] = min(self._route_count_table[route_id]["mn"], request_time)
            self._route_count_table[route_id]["t"] = ((self._route_count_table[route_id]["t"] * (
                self._route_count_table[route_id]["c"] - 1)) + request_time) / self._route_count_table[route_id]["c"]
        finally:
            requestCountLock.release()
