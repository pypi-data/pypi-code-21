#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/1/4
 """
from __future__ import unicode_literals, absolute_import
import jpush
from djdg_core.apis.jg.public import client
import logging
import json


logger = logging.getLogger('jpush')


def notification(alert, alias, platform=jpush.all_):
    """
    极光推送通知
    :param alert:
    :param alias: [phone number, ]
    :param platform:
    :return:
    """
    push = client.create_push()
    push.audience = jpush.audience(jpush.alias(alias))
    push.notification = jpush.notification(alert=alert)
    push.platform = platform
    res = push.send()
    logger.info('status code {}, response {}'.format(
        res.get_status_code(),
        json.dumps(res.payload)
    ))
    return res
