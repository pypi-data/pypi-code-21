#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertisers.
"""

import logging

from pyhttpstatus_utils import (HttpStatusType, is_http_status_type)
from requests_mv_integrations.support import (validate_json_response)
from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from tune_reporting.errors import (print_traceback, get_exception_message, TuneReportingErrorCodes)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import (python_check_version)
from tune_reporting import (__python_required_version__)
from tune_reporting.tmc.tune_mobileapptracking_api_base import (TuneMobileAppTrackingApiBase)
from logging_mv_integrations import (LoggingFormat, LoggingOutput)
# from pprintpp import pprint

python_check_version(__python_required_version__)


# @brief TUNE Advertisers.
#
# @namespace tune_reporting.TuneV2AdvertiserStatus
class TuneV2AdvertiserStatus(object):
    """Status states for Advertisers.
    """
    ACTIVE = 1
    NOT_ACTIVE = 2
    ALL = 3


#   TUNE MobileAppTracking: Advertisers
#
class TuneV2Advertisers(TuneMobileAppTrackingApiBase):
    """TUNE Advertisers.
    """

    #  Advertiser ID
    #  @var str
    __advertiser_id = None

    # Initialize Job
    #
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR
    ):
        super(TuneV2Advertisers, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

    @property
    def advertiser_id(self):
        """Get Property: advertiser_id
        """
        return self.__advertiser_id

    @advertiser_id.setter
    def advertiser_id(self, value):
        """Set Property: advertiser_id
        """
        self.__advertiser_id = value

    # Collect Advertisers
    #
    def get_advertiser_id(self, auth_type, auth_value, request_retry=None):
        """Get Advertiser ID

        Args:
            auth_type:
            auth_value:
            request_retry:

        Returns:

        """
        if not auth_type:
            raise ValueError("TMC v2 Advertisers: Get Advertiser ID: Value 'auth_type' not provided.")
        if not auth_value:
            raise ValueError("TMC v2 Advertisers: Get Advertiser ID: Value 'auth_value' not provided.")

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller="advertiser",
                action="find"
            )

        request_params = {auth_type: auth_value}

        self.logger.info("TMC v2 Advertisers: Advertiser ID")

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_retry=None,
                request_retry_http_status_codes=None,
                request_retry_func=self.tune_v2_request_retry_func,
                request_retry_excps_func=None,
                request_label="TMC v2 Advertisers"
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v2 Advertisers: Advertiser ID: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v2 Advertisers: Advertiser ID: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error(
                "TMC v2 Advertisers: Advertiser ID: Failed",
                extra={'error': get_exception_message(ex)},
            )

            raise TuneReportingError(
                error_message=("TMC v2 Advertisers: Failed: {}").format(get_exception_message(ex)),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v2 Advertisers: Advertiser ID:"
        )

        self.logger.debug("TMC v2 Advertisers: Advertiser ID", extra={'response': json_response})

        json_response_status_code = json_response['status_code']

        http_status_successful = is_http_status_type(
            http_status_code=json_response_status_code, http_status_type=HttpStatusType.SUCCESSFUL
        )

        if not http_status_successful or not json_response['data']:
            raise TuneReportingError(
                error_message="TMC v2 Advertisers: Failed: {}".format(json_response_status_code),
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        if 'data' not in json_response or \
                not json_response['data'] or \
                len(json_response['data']) == 0:
            raise TuneReportingError(
                error_message="TMC v2 Advertisers: Advertiser ID: Failed",
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        advertiser_data = json_response['data'][0]

        self.advertiser_id = advertiser_data.get('id', None)
        if self.advertiser_id is None:
            raise TuneReportingError(
                error_message="TMC v2 Advertisers: Advertiser ID: Failed",
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        self.logger.info("TMC v2 Advertisers: Advertiser ID: {}".format(self.advertiser_id))

        return True
