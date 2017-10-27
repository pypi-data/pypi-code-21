# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.policies import TCellPolicy

import logging

logger = logging.getLogger('tcell_agent').getChild(__name__)


class SecureHeader:
    approved_headers = [
        "strict-transport-security",
        "x-frame-options",
        "x-xss-protection",
        "x-content-type-options",
        "x-permitted-cross-domain-policies",
        "x-download-options"
    ]

    def __init__(self, name, value):
        if name.lower() not in self.approved_headers:
            raise Exception("Header name is not in approved list: " + name)
        self.name = name
        self.value = value

    def header_value(self):
        return self.value


class SecureHeadersPolicy(TCellPolicy):
    def __init__(self, policy_json=None):
        super(SecureHeadersPolicy, self).__init__()
        self.secure_headers = []
        if policy_json is not None:
            self.load_from_json(policy_json)

    def headers(self):
        headers = []
        for header in self.secure_headers:
            headers.append([header.name, header.value])
        return headers

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")
        secure_headers = []
        if "headers" in policy_json:
            for header in policy_json["headers"]:
                if "name" in header and "value" in header:
                    try:
                        secure_header = SecureHeader(header["name"], header["value"])
                        secure_headers.append(secure_header)
                    except:
                        logger.error("error parsing secure header (%s, %s)" % (header["name"], header["value"]))
        self.secure_headers = secure_headers
