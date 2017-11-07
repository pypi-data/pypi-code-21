# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.policies import TCellPolicy


class HttpTxPolicy(TCellPolicy):
    def __init__(self, policy_json=None):
        super(HttpTxPolicy, self).__init__()
        self.firehose = {"enabled": False, "lite": False}
        self.auth_framework = {"enabled": False, "lite": False}
        self.profile = {"enabled": False}
        self.fingerprint = {"enabled": False}

        if policy_json is not None:
            self.load_from_json(policy_json)

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        self.firehose = {"enabled": False, "lite": False}
        self.auth_framework = {"enabled": False, "lite": False}
        self.profile = {"enabled": False}
        self.fingerprint = {"enabled": False, "hmacUserAgent": False, "hmacUserId": False, "sampling": 0}

        types = policy_json.get("types")
        if types:
            firehose_settings = types.get("firehose")
            if firehose_settings:
                self.firehose["enabled"] = firehose_settings.get("enabled", False)
                self.firehose["lite"] = firehose_settings.get("lite", False)
            if types.get("auth_framework"):
                self.auth_framework["enabled"] = types.get("auth_framework").get("enabled", False)
                self.auth_framework["lite"] = types.get("auth_framework").get("lite", False)
            if types.get("profile"):
                self.profile["enabled"] = types.get("profile").get("enabled", False)
            if types.get("fingerprint"):
                self.fingerprint["enabled"] = types.get("fingerprint").get("enabled", False)
                self.fingerprint["hmacUserAgent"] = types.get("fingerprint").get("hmacUserAgent", False)
                self.fingerprint["hmacUserId"] = types.get("fingerprint").get("hmacUserId", False)
                self.fingerprint["sampling"] = types.get("fingerprint").get("sampling", 0)
