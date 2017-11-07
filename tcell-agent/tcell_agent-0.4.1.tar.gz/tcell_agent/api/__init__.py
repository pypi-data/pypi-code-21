# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" API Module handles all calls to/from the tCell service. Errors are
handled gracefully since it's generally running silently and should
fail open.
"""

from __future__ import unicode_literals

import json
import logging
import sys
import requests

from tcell_agent.config import CONFIGURATION
from tcell_agent.version import VERSION

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

    def encode(self, obj):
        def traverse(obj):
            if isinstance(obj, dict):
                return {k: traverse(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [traverse(elem) for elem in obj]
            elif (isinstance(obj, str) or isinstance(obj, bytes) or
                  (sys.version_info < (3, 0) and isinstance(obj, unicode))) and len(obj) > 256:
                return obj[:256]
            else:
                return obj  # no container, just values (str, int, float)
        return super(SetEncoder, self).encode(traverse(obj))


class TCellAPIException(Exception):
    """Special API Exception"""
    pass


class TCellAPI(object):
    """API Class handling comms"""

    def v1update(self, last_timestamp=None):
        """v1 is the new rest API endpoint"""
        url = '{url}/app/{appname}/update'.format(
            url=CONFIGURATION.tcell_api_url,
            appname=CONFIGURATION.app_id)
        LOGGER.debug("calling api: %s", url)
        params = {}
        if last_timestamp:
            params["last_timestamp"] = last_timestamp
        headers = {"Authorization": "Bearer " + CONFIGURATION.api_key,
                   "TCellAgent": "Python " + VERSION}
        try:
            response = requests.get(url, params=params, headers=headers, allow_redirects=False)
        except Exception as general_exception:
            LOGGER.error("Error connecting to tcell: {e}".format(e=general_exception))
            LOGGER.debug(general_exception, exc_info=True)
            raise TCellAPIException("could not connect to server")

        LOGGER.debug("response: %s", response)

        if response.ok:
            try:
                response_json = response.json()
                return response_json.get("result", None)
            except Exception as general_exception:
                LOGGER.error("Error parsing tcell response: {e}".format(e=general_exception))
                LOGGER.debug(general_exception, exc_info=True)
                raise TCellAPIException("Error parsing tcell response")

        raise TCellAPIException("Response was not 'ok'")

    def v1send_events(self, events):
        """
        Sends events to tCell via the API
        v1 is the new rest API
        """
        event_endpoint = "server_agent"
        url = '{url}/app/{appname}/{endpoint}'.format(
            url=CONFIGURATION.tcell_input_url,
            appname=CONFIGURATION.app_id,
            endpoint=event_endpoint)
        payload = {"hostname": CONFIGURATION.host_identifier,
                   "uuid": CONFIGURATION.uuid,
                   "events": events}
        LOGGER.debug("sending events to %s", url)
        LOGGER.debug(json.dumps(payload, cls=SetEncoder))
        headers = {"Authorization": "Bearer " + CONFIGURATION.api_key,
                   "Content-type": "application/json",
                   "TCellAgent": "Python " + VERSION}
        response = requests.post(url, data=json.dumps(payload, cls=SetEncoder), headers=headers, allow_redirects=False)
        LOGGER.debug("send_events response: [%s]", response.status_code)
        return response.status_code
