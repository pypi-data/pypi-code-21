# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging

from .runtime_infos import RuntimeInfos, runtime

LOGGER = logging.getLogger(__name__)


class PayloadCreator(object):
    """Create attack payloads."""

    SECTIONS = (
        'request',
        'params',
        'headers',
        'local',
        'rule',
        'context',
    )

    def __init__(self, sections=None):
        if sections is None:
            self.sections = self.SECTIONS
        else:
            for section in sections:
                if section not in self.SECTIONS:
                    LOGGER.warning("Unknown section %r, fallback to "
                                   "default sections", section)
                    self.sections = self.SECTIONS
                    break
            else:
                self.sections = sections

    def get_payload(self, rule_name, rulespack_id, test, context_payload=None):
        current_request = runtime.get_current_request()
        if current_request is None:
            LOGGER.warning("No request was recorded, cannot create payload")
            return
        payload = {}
        if 'request' in self.sections:
            payload['request'] = current_request.request_payload
        if 'params' in self.sections:
            payload['params'] = current_request.request_params
        if 'headers' in self.sections:
            payload['headers'] = current_request.get_client_ips_headers()
        if 'local' in self.sections:
            payload['local'] = RuntimeInfos.local_infos()
        if 'rule' in self.sections:
            payload['rule'] = {
                'name': rule_name,
                'rulespack_id': rulespack_id,
                'test': test,
            }
        if 'context' in self.sections:
            if context_payload is None:
                context_payload = {
                    'context': {
                        'backtrace': list(current_request.raw_caller)
                    }
                }
            payload.update(context_payload)
        return payload
