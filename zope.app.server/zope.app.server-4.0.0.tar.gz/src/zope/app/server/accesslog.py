##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Configuration support for the access log.

This assumes that access logging is being performed through the logger
object returned by logging.getLogger('accesslog').
"""
import logging

from ZConfig.components.logger.logger import LoggerFactoryBase


class AccessLogFactory(LoggerFactoryBase):
    """Logger factory that returns the access logger."""

    name = "accesslog"

    def create(self):
        logger = LoggerFactoryBase.create(self)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        formatter = logging.Formatter()
        for handler in logger.handlers:
            handler.setFormatter(formatter)
        return logger
