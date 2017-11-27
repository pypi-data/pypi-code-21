#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.util.sentry
    ~~~~~~~~~~~~

    This module provide the sentry client.

    :copyright: (c) 2017 by Ma Fei.
"""
from raven import Client

from agent.config import sentry_url


class Sentry(object):
    @property
    def client(self):
        return Client(sentry_url.get('url'))
