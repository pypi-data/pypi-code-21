# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for badly behaved clients
"""
from logging import getLogger

from ..runtime_infos import runtime
from .regexp_rule import RegexpRule

LOGGER = getLogger(__name__)


class UserAgentMatchesCBFramework(RegexpRule):

    def pre(self, original, *args, **kwargs):

        request = runtime.get_current_request()

        if not request:
            LOGGER.warning("No request was recorded abort")
            return

        user_agent = request.client_user_agent
        if not user_agent:
            return

        match = self.match_regexp(user_agent)
        if not match:
            return

        infos = {'found': match}
        self.record_attack(infos)

        return {'status': 'raise', 'data': match,
                'rule_name': self.rule_name}


UserAgentMatchesCBDjango = UserAgentMatchesCBFramework
