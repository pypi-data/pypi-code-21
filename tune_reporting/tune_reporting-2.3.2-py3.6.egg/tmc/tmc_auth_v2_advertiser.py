#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""
TUNE Multiverse Reporting Base
================================
"""

import logging
from pprintpp import pprint

from requests_mv_integrations.exceptions import (TuneRequestBaseError)

from logging_mv_integrations import (LoggingFormat, LoggingOutput)

from tune_reporting.errors import (get_exception_message, print_traceback, TuneReportingErrorCodes)
from tune_reporting.exceptions import (TuneReportingError, TuneReportingAuthError)
from tune_reporting.support import (base_class_name)
from tune_reporting.tmc.v2.management.tmc_v2_advertisers import (TuneV2Advertisers)
from tune_reporting.tmc.v2.management.tmc_v2_session_authenticate import (TuneV2AuthenticationTypes)

log = logging.getLogger(__name__)


def tmc_auth_v2_advertiser(
    tmc_api_key,
    logger_level=logging.NOTSET,
    logger_format=LoggingFormat.JSON,
    logger_output=LoggingOutput.STDOUT_COLOR
):
    """TMC Authentication

    :return:
    """
    log.info("TMC v2 Advertiser: Authentication: Start")

    response_auth = None

    tune_v2_advertisers = \
        TuneV2Advertisers(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

    try:
        try:
            if tune_v2_advertisers.get_advertiser_id(
                auth_type=TuneV2AuthenticationTypes.API_KEY,
                auth_value=tmc_api_key,
                request_retry=None
            ):
                advertiser_id = tune_v2_advertisers.advertiser_id

                log.debug("TMC v2 Advertiser: {}".format(advertiser_id))

        except TuneRequestBaseError as tmc_req_ex:
            pprint(tmc_req_ex.to_dict())
            print(str(tmc_req_ex))

        except TuneReportingError as tmc_rep_ex:
            pprint(tmc_rep_ex.to_dict())
            print(str(tmc_rep_ex))

        except Exception as ex:
            print_traceback(ex)
            print(get_exception_message(ex))

    except Exception as ex:
        print_traceback(ex)
        error_code = TuneReportingErrorCodes.REP_ERR_SOFTWARE

        log.error(
            'TMC v2 Advertiser: Authentication: Failed: Unexpected',
            extra={
                'exit_code': error_code,
                'error_exception': base_class_name(ex),
                'error_details': get_exception_message(ex)
            }
        )

        raise TuneReportingAuthError(
            error_message="TMC v2 Advertiser: Authentication: Failed: Unexpected", errors=ex, error_code=error_code
        )

    if response_auth:
        log.debug("TMC v2 Advertiser: Authentication: Details", extra=response_auth.to_dict())

    return response_auth
