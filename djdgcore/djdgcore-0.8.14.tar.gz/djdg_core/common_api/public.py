#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.rest_client import RestClient
from djdg_core import settings
import logging


logger = logging.getLogger(settings.LOGGER_NAME)


common_client = RestClient(
    host=settings.COMMON_API_HOST,
    base_url=settings.COMMON_API_BASE_URL,
    protocol=settings.COMMON_API_PROTOCOL,
    logger=logger,
    oauth_app_id=settings.COMMON_API_AUTH_APP_ID,
    oauth_app_secret=settings.COMMON_API_AUTH_APP_SECRET
)
