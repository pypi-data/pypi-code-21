# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging

from future.backports.urllib.parse import quote_plus

from tcell_agent.config import CONFIGURATION
from tcell_agent.policies import TCellPolicy
from tcell_agent.sanitize.sanitize_utils import java_hash

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


# Easy test mocking
def get_logger():
    return LOGGER


def string_bytesize(val):
    try:
        return len(val.encode('utf-8'))
    except:
        return len(val)


class ContentSecurityHeader:
    def __init__(self, csp_type, value, report_uri=None, policy_id=None):
        self.csp_type = None
        self.value = None
        self.policy_id = None
        if csp_type is not None:
            if csp_type.lower() == "content-security-policy":
                self.csp_type = "csp"
            elif csp_type.lower() == "content-security-policy-report-only":
                self.csp_type = "csp-report"
            elif csp_type == "csp" or csp_type == "csp-report":
                self.csp_type = csp_type
            else:
                raise Exception("Unknown header")
        self.report_uri = report_uri
        self.value = value
        self.policy_id = policy_id

    def header_value(self, transaction_id=None, route_id=None, session_id=None, user_id=None):
        if self.report_uri is None:
            return self.value
        try:
            query_parts = []
            if transaction_id:
                query_parts.append("tid=" + quote_plus(transaction_id))
            if session_id:
                query_parts.append("sid=" + quote_plus(session_id))
            if route_id:
                query_parts.append("rid=" + quote_plus(route_id))

            if len(query_parts) > 0:
                report_url = self.report_uri + "?" + "&".join(query_parts)
            else:
                report_url = self.report_uri

            if self.policy_id is not None:
                checksum = str(java_hash(self.policy_id + report_url))
                if len(query_parts) > 0:
                    report_url = report_url + "&"
                else:
                    report_url = report_url + "?"
                report_url = report_url + "c=" + checksum
            return "%s; report-uri %s" % (self.value, report_url)
        except Exception as e:
            get_logger().debug("error creating csp: %s: (%s, %s), falling back" % (e, self.value, self.report_uri))
            return "%s; report-uri %s" % (self.value, self.report_uri)

    def header_names(self):
        if self.csp_type == "csp":
            return ["Content-Security-Policy"]
        elif self.csp_type == "csp-report":
            return ["Content-Security-Policy-Report-Only"]
        else:
            return []


class ContentSecurityPolicy(TCellPolicy):
    def __init__(self, policy_json=None, header_class=ContentSecurityHeader):
        super(ContentSecurityPolicy, self).__init__()
        self.header_class = header_class
        self.csp_headers = []
        self.js_agent_api_key = None
        if policy_json is not None:
            self.load_from_json(policy_json)

    def loadFromHeaderString(self, header_string):
        if header_string is not None:
            csp_header_split = header_string.split(":", 1)
            csp_headers = []
            try:
                csp_header = self.header_class(csp_header_split[0], csp_header_split[1])
                csp_headers.append(csp_header)
            except:
                get_logger().error("error parsing secure header (%s)" % (header_string))
            self.csp_headers = csp_headers

    def headers(self, transaction_id=None, route_id=None, session_id=None, user_id=None, path_info=None):
        headers = []
        for header in self.csp_headers:
            header_value = header.header_value(transaction_id, route_id, session_id, user_id)
            if CONFIGURATION.max_csp_header_bytes is None or string_bytesize(header_value) <= CONFIGURATION.max_csp_header_bytes:
                for header_name in header.header_names():
                    headers.append([header_name, header_value])
            else:
                get_logger().warn(
                    "[RouteId={route_id},Path={path}] CSP header({header_value_size}) is bigger than configured max_csp_header_bytes({max_csp_header_bytes})".
                    format(route_id=route_id,
                           path=path_info,
                           header_value_size=string_bytesize(header_value),
                           max_csp_header_bytes=CONFIGURATION.max_csp_header_bytes))

        return headers

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")
        csp_headers = []
        self.js_agent_api_key = None
        if "data" in policy_json:
            if "options" in policy_json["data"]:
                policy_option_json = policy_json["data"]["options"]
                if policy_option_json:
                    self.js_agent_api_key = policy_option_json.get("js_agent_api_key", None)

        if "headers" in policy_json:
            CONFIGURATION.js_agent_url = CONFIGURATION.startup_js_agent_url

            for header in policy_json["headers"]:
                if "name" in header and "value" in header:
                    try:
                        if "https://jsagent.tcell.io" in header[
                            "value"] and CONFIGURATION.startup_js_agent_url == "https://api.tcell.io/tcellagent.min.js":
                            CONFIGURATION.js_agent_url = "https://jsagent.tcell.io/tcellagent.min.js"

                        csp_header = self.header_class(header["name"], header["value"], header.get("report-uri"),
                                                       self.policy_id)
                        csp_headers.append(csp_header)
                    except Exception as e:
                        get_logger().error("error parsing csp header (%s, %s)" % (header["name"], header["value"]))

        self.csp_headers = csp_headers
