#!/usr/bin/env python
# -*- coding: utf-8 -*-
from raven import Client

from agent.config import sentry_url


class Sentry(object):
    @property
    def client(self):
        return Client(sentry_url.get('url'))
