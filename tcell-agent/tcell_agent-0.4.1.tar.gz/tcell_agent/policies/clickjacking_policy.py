# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.policies.content_security_policy import ContentSecurityPolicy, ContentSecurityHeader


class ClickjackingHeader(ContentSecurityHeader):
    def __init__(self, csp_type, value, report_uri=None, policy_id=None):
        self.csp_type = None
        self.value = None
        self.policy_id = None
        if (csp_type is not None):
            if (csp_type.lower() == "content-security-policy"):
                self.csp_type = "csp"
            elif (csp_type == "csp"):
                self.csp_type = csp_type
            else:
                raise Exception("Unknown header")
        self.report_uri = report_uri
        self.value = value


class ClickjackingPolicy(ContentSecurityPolicy):
    def __init__(self, policy_json=None):
        super(ClickjackingPolicy, self).__init__(policy_json, header_class=ClickjackingHeader)
