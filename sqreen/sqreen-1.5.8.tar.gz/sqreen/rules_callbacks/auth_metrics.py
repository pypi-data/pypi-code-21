# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Aggregate authentication tentatives
"""
import json
import logging

from ..runtime_infos import runtime
from ..utils import CustomJSONEncoder
from .matcher_callback import MatcherRule

LOGGER = logging.getLogger(__name__)


class AuthMetricsCB(MatcherRule):

    def post(self, original, result, *args, **kwargs):
        # Django authentication model return either an User or None
        if result is None:
            auth_status = 'auto-login-fail'
        else:
            auth_status = 'auto-login-success'

        keys = []

        # Search for credentials identifier that match the whitelist
        for identifier in kwargs.keys():
            if self.match(identifier):
                keys.append([identifier.lower(), kwargs[identifier]])

        if not keys:
            # If we couldn't identify an user, don't record a metric
            return

        request = runtime.get_current_request()
        if not request:
            LOGGER.warning("No request was recorded, abort")
            return
        key = {'keys': keys, 'ip': request.client_ip}

        observation_key = json.dumps(key, separators=(',', ':'), sort_keys=True,
                                     cls=CustomJSONEncoder)
        self.record_observation(auth_status, observation_key, 1)
