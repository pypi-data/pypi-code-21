#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations


# @brief TUNE Logging Format ENUM
#
# @namespace logging_mv_integrations.TuneLoggingFormat
class TuneLoggingFormat(object):
    """TUNE Logging Format ENUM
    """
    STANDARD = "standard"
    JSON = "json"

    @staticmethod
    def validate(value):
        if not value or value is None:
            return False
        if value in [TuneLoggingFormat.STANDARD, TuneLoggingFormat.JSON]:
            return True
        return False
