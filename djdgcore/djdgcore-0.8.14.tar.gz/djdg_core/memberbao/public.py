#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/3
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.rest_client import RestClient
from djdg_core import settings
import logging


logger = logging.getLogger(settings.LOGGER_NAME)


memberbao_client = RestClient(
    settings.MEMBERBAO_HOST,
    settings.MEMBERBAO_BASE_URL,
    settings.MEMBERBAO_PROTOCOL,
    oauth_app_id=settings.MEMBERBAO_AUTH_APP_ID,
    oauth_app_secret=settings.MEMBERBAO_AUTH_APP_SECRET,
    logger=logger
)
