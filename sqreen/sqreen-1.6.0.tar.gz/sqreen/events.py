# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen attack event helpers and placeholder
"""
import traceback
from logging import getLogger

from .remote_exception import traceback_formatter

LOGGER = getLogger(__name__)


def get_context_payload():
    """ Return attack payload dependent on the context, right now stacktrace.
    """
    return {
        'context': {
            'backtrace': list(traceback_formatter(traceback.extract_stack()))
        }
    }


class Attack(object):

    def __init__(self, payload, rule_name):
        self.payload = payload
        self.rule_name = rule_name

    def to_dict(self):
        result = {}
        rule_payload = self.payload.get('rule', {})
        request_payload = self.payload.get('request', {})
        local_payload = self.payload.get('local', {})
        if 'name' in rule_payload:
            result['rule_name'] = rule_payload['name']
        if 'rulespack_id' in rule_payload:
            result['rulespack_id'] = rule_payload['rulespack_id']
        if 'test' in rule_payload:
            result['test'] = rule_payload['test']
        if 'infos' in self.payload:
            result['infos'] = self.payload['infos']
        if 'time' in local_payload:
            result['time'] = local_payload['time']
        if 'addr' in request_payload:
            result['client_ip'] = request_payload['addr']
        if 'request' in self.payload:
            result['request'] = self.payload['request']
        if 'params' in self.payload:
            result['params'] = self.payload['params']
        if 'context' in self.payload:
            result['context'] = self.payload['context']
        if 'headers' in self.payload:
            result['headers'] = self.payload['headers']
        return result
