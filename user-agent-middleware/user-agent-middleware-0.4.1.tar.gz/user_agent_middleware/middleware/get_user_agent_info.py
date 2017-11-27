# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
import logging

from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject

from user_agent_middleware.utils import get_user_agent

User = get_user_model()
logger = logging.getLogger('system')


if django.VERSION >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object


class VisitorSiteMiddlewareClass(MiddlewareMixin):

    def process_request(self, request):
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
