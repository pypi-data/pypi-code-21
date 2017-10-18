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

    def __init__(self, payload):
        self.payload = payload
        self.rule_name = payload['rule_name']

    def to_dict(self):
        return self.payload
