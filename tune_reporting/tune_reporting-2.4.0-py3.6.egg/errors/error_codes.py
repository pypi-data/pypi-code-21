#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting.errors

from requests_mv_integrations.errors import (TuneRequestErrorCodes)


class TuneReportingErrorCodes(TuneRequestErrorCodes):
    """TUNE Reporting Error Codes
    """

    REP_ERR_UNASSIGNED = -1

    MOD_OK = 0  # Success

    #
    # 7xx Tune Reporting Errors
    #
    REP_ERR_REPORTING = 700  # Reporting Error

    REP_ERR_REQUEST = 707
    # Exit code that request failed.

    REP_ERR_SOFTWARE = 708
    # Exit code that means an internal
    # software error was detected.

    REP_ERR_UNEXPECTED_VALUE = 710
    # Unexpected value either
    # returned or null.

    REP_ERR_JOB_STOPPED = 721  # Job Stopped
    REP_ERR_RETRY_EXHAUSTED = 722  # Retry Exhausted

    REP_ERR_AUTH_ERROR = 760  # Auth Error
    REP_ERR_AUTH_JSON_ERROR = 761  # Auth JSON Error

    REP_ERR_JSON_DECODING = 766  # JSON Decoding Error

    REP_ERR_UNEXPECTED = 799  # Unexpected Error
