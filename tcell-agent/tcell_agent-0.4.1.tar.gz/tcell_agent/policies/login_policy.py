# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from tcell_agent.policies import TCellPolicy


class LoginPolicy(TCellPolicy):
    api_identifier = "login"

    def __init__(self, policy_json=None):
        super(LoginPolicy, self).__init__()
        self.init_variables()
        if policy_json is not None:
            self.load_from_json(policy_json)

    def init_variables(self):
        self.login_failed_enabled = False
        self.login_success_enabled = False
        self.session_hijacking_metrics = False

    def is_enabled(self):
        return self.login_success_enabled or self.login_failed_enabled

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")
        self.init_variables()
        policy_data = policy_json.get("data")
        if policy_data:
            options_json = policy_data.get("options")
            if options_json:
                self.login_failed_enabled = options_json.get("login_failed_enabled", False)
                self.login_success_enabled = options_json.get("login_success_enabled", False)
                self.session_hijacking_metrics = options_json.get("session_hijacking_enabled", False)
