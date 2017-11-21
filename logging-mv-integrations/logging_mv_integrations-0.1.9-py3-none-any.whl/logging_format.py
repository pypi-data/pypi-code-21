#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations


# @brief TUNE Logging Format ENUM
#
# @namespace logging_mv_integrations.LoggingFormat
class LoggingFormat(object):
    """TUNE Logging Format ENUM
    """
    STANDARD = "standard"
    JSON = "json"

    @staticmethod
    def validate(value):
        if not value or value is None:
            return False
        if value in [LoggingFormat.STANDARD, LoggingFormat.JSON]:
            return True
        return False
