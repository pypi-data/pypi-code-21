#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations


# @brief TUNE Logging Output ENUM
#
# @namespace logging_mv_integrations.LoggingOutput
class LoggingOutput(object):
    """TUNE Logging Output ENUM
    """
    STDOUT = "stdout"
    STDOUT_COLOR = "color"
    FILE = "file"

    @staticmethod
    def validate(value):
        if not value or value is None:
            return False
        if value in [LoggingOutput.STDOUT, LoggingOutput.STDOUT_COLOR, LoggingOutput.FILE]:
            return True
        return False
