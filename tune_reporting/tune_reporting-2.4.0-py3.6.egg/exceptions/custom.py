#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""
Tune Reporting Error
"""

from tune_reporting.errors import (TuneReportingErrorCodes)
from .base import (TuneReportingBaseError)


class TuneReportingError(TuneReportingBaseError):
    pass


class TuneReportingAuthError(TuneReportingBaseError):
    def __init__(self, **kwargs):
        error_code = kwargs.pop('error_code', None) or TuneReportingErrorCodes.REP_ERR_AUTH_ERROR
        super(TuneReportingAuthError, self).__init__(error_code=error_code, **kwargs)
