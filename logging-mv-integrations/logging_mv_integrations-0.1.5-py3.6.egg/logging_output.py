#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations


# @brief TUNE Logging Output ENUM
#
# @namespace logging_mv_integrations.TuneLoggingOutput
class TuneLoggingOutput(object):
    """TUNE Logging Output ENUM
    """
    STDOUT = "stdout"
    STDOUT_COLOR = "color"
    FILE = "file"
    TEST = "test"

    @staticmethod
    def validate(value):
        if not value or value is None:
            return False
        if value in [TuneLoggingOutput.STDOUT, TuneLoggingOutput.STDOUT_COLOR, TuneLoggingOutput.FILE, TuneLoggingOutput.TEST]:
            return True
        return False
