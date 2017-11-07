#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""
TUNE Multiverse Reporting Base
================================
"""

import logging

from logging_mv_integrations import (LoggingFormat, LoggingOutput)

from tune_reporting.errors import (
    get_exception_message,
    print_traceback,
)
from tune_reporting.exceptions import (TuneReportingAuthError, TuneReportingError)
from tune_reporting.support import (base_class_name)
from tune_reporting.tmc.v2.management.tmc_v2_session_authenticate import (TuneV2SessionAuthenticate)

log = logging.getLogger(__name__)


def tmc_auth_v2_session_token(
    tmc_api_key,
    logger_level=logging.NOTSET,
    logger_format=LoggingFormat.JSON,
    logger_output=LoggingOutput.STDOUT_COLOR
):
    """TMC Authentication

    :return:
    """
    log.info("TMC v2 Session Token: Request")

    try:
        tune_v2_session_authenticate = \
            TuneV2SessionAuthenticate(
                logger_level=logger_level,
                logger_format=logger_format,
                logger_output=logger_output
            )

        if tune_v2_session_authenticate.get_session_token(tmc_api_key=tmc_api_key, request_retry=None):
            session_token = tune_v2_session_authenticate.session_token

    except TuneReportingError as auth_ex:
        log.error("TMC v2 Session Token: Failed", extra=auth_ex.to_dict())

        raise

    except Exception as ex:
        print_traceback(ex)
        log.error(
            'TMC v2 Session Token: Failed: Unexpected',
            extra={'error_exception': base_class_name(ex),
                   'error_details': get_exception_message(ex)}
        )

        raise TuneReportingAuthError(
            error_message="TMC v2 Session Token: Failed: Unexpected",
            errors=ex,
        )

    log.debug("TMC v2 Session Token: Response", extra={'session_token': session_token})

    return session_token
