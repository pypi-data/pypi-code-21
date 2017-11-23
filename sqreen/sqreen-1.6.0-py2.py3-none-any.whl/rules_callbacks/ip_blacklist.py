# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging

from ..list_filters import IPNetworkListFilter
from ..rules import RuleCallback
from ..runtime_infos import runtime

LOGGER = logging.getLogger(__name__)


class IPBlacklistCB(RuleCallback):

    def __init__(self, *args, **kwargs):
        super(IPBlacklistCB, self).__init__(*args, **kwargs)
        self.networks = IPNetworkListFilter(self.data['values'])
        LOGGER.debug('Blacklisted IP networks: %s', self.networks)

    def pre(self, original, *args, **kwargs):
        request = runtime.get_current_request()
        if request is None:
            return
        network = self.networks.match(request.client_ip)
        if network is None:
            LOGGER.debug("IP %s is not blacklisted", request.client_ip)
            return
        LOGGER.debug("IP %s belongs to blacklisted network %s",
                     request.client_ip, network)
        self.record_observation('blacklisted', network, 1)
        return {
            'status': 'raise',
            'data': network,
            'rule_name': self.rule_name,
        }
