#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE MobileAppTracking API base class
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

python_check_version(__python_required_version__)


# @brief TUNE Authentication Types ENUM
#
# @namespace tune_reporting.TuneV2AuthenticationTypes
class TuneV2AuthenticationTypes(object):
    """TUNE Authentication Types ENUM
    """
    API_KEY = "api_key"
    SESSION_TOKEN = "session_token"

    @staticmethod
    def validate(auth_type):
        return auth_type in [
            TuneV2AuthenticationTypes.API_KEY,
            TuneV2AuthenticationTypes.SESSION_TOKEN,
        ]


# @brief  TUNE MobileAppTracking API v2/session/authenticate
#
# @namespace tune_reporting.TuneV2SessionAuthenticate
class TuneV2SessionAuthenticate(TuneMobileAppTrackingApiBase):
    """TUNE MobileAppTracking API v2/session/authenticate
    """

    # Initialize Job
    #
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR
    ):
        super(TuneV2SessionAuthenticate, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

    def get_session_token(self, tmc_api_key, request_retry=None):
        """Generate session token is returned to provide
        access to service.

        Args:
            tmc_api_key:
            request_retry:

        Returns:

        """
        self.logger.info("TMC v2 Session Authenticate: Get Token")

        self.api_key = tmc_api_key

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller="session/authenticate",
                action="api_key"
            )

        request_params = \
            {
                'api_keys': tmc_api_key,
                "source": "multiverse"
            }

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_retry=None,
                request_retry_http_status_codes=None,
                request_retry_func=self.tune_v2_request_retry_func,
                request_retry_excps_func=None,
                request_label="TMC v2 Session Authenticate"
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v2 Session Authenticate: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v2 Session Authenticate: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TMC v2 Session Authenticate: Failed: {}".format(get_exception_message(ex)))

            raise TuneReportingError(
                error_message=("TMC v2 Session Authenticate: Failed: {}").format(get_exception_message(ex)),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v2 Get Session Token: Validate",
        )

        self.logger.debug(
            "TMC v2 Session Authenticate: Details:",
            extra={'response': json_response},
        )

        response_status_code = json_response.get('status_code', None)
        status_code_successful = is_http_status_type(
            http_status_code=response_status_code, http_status_type=HttpStatusType.SUCCESSFUL
        )

        response_errors = json_response.get('errors', None)

        response_error_message = ""
        if response_errors:
            if isinstance(response_errors, dict):
                error_message = response_errors.get('message', None)
                if error_message:
                    if error_message.startswith("Invalid api key"):
                        response_status_code = TuneReportingErrorCodes.UNAUTHORIZED
                    response_error_message += error_message
            elif isinstance(response_errors, list):
                for response_error in response_errors:
                    if isinstance(response_error, dict) \
                            and 'message' in response_error:
                        error_message = response_error.get('message', None)
                        if error_message:
                            if error_message.startswith("Invalid api key"):
                                response_status_code = TuneReportingErrorCodes.UNAUTHORIZED
                            response_error_message += error_message

        error_code = response_status_code

        if not status_code_successful or not json_response['data']:
            raise TuneReportingError(
                error_message="TMC v2 Session Authenticate: Failed: {}".format(response_error_message),
                error_code=error_code,
            )

        self.session_token = json_response['data']

        self.logger.info("TMC v2 Session Authenticate", extra={'session_token': self.session_token})
        self.logger.info("TMC v2 Session Authenticate: Finished")

        return True
