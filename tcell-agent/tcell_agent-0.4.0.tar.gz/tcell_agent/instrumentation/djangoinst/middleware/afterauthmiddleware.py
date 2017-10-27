# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.sanitize import SanitizeUtils
from tcell_agent.instrumentation import safe_wrap_function


def add_user_and_session(request):
    try:
        if hasattr(request, 'user') and request.user.is_authenticated() and request.user.id:
            uid = request.user.id
            if uid is not None:
                uid = str(uid)
            request._tcell_context.user_id = uid
    except:
        pass

    if hasattr(request, 'session') and hasattr(request.session, 'session_key'):
        request._tcell_context.raw_session_id = request.session.session_key
        request._tcell_context.session_id = SanitizeUtils.hmac_half(request.session.session_key)


class AfterAuthMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        return self.get_response(request)

    def process_request(self, request):
        safe_wrap_function("Initizating Request", add_user_and_session, request)
