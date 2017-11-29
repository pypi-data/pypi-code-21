#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TMC API Base class
"""

import logging
import requests
import datetime as dt
# from pprintpp import pprint

from pytz_convert import (validate_tz_name)
from pyhttpstatus_utils import (http_status_code_to_type)
from tune_reporting.support import (
    python_check_version,
    __TIMEZONE_NAME_DEFAULT__,
)
from tune_reporting.errors import (
    print_traceback,
    get_exception_message,
    TuneReportingErrorCodes,
)
from requests_mv_integrations.exceptions import (
    TuneRequestBaseError,
    TuneRequestError
)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting import (__version__, __python_required_version__)
from requests_mv_integrations import (RequestMvIntegrationDownload)
from tune_reporting.support import (command_line_request_curl_get)
from logging_mv_integrations import (
    LoggingFormat,
    LoggingOutput,
    get_logger
)
from safe_cast import safe_str

python_check_version(__python_required_version__)


# @brief  TUNE MobileAppTracking API base class
#
# @namespace tune_reporting.TuneMobileAppTrackingApiBase
class TuneMobileAppTrackingApiBase(object):
    """TUNE MobileAppTracking API base class
    """

    _TUNE_MANAGEMENT_API_ENDPOINT = "https://api.mobileapptracking.com"

    __tmc_credentials = None
    __timezone = None
    __mv_request = None
    __logger = None

    @property
    def mv_request(self):
        """Get Property: Logger
        """
        if self.__mv_request is None:
            self.__mv_request = RequestMvIntegrationDownload(
                logger_format=self.logger_format,
                logger_level=self.logger_level,
                logger_output=self.logger_output
            )

        return self.__mv_request

    @property
    def logger(self):
        """Get Property: Logger
        """
        if self.__logger is None:
            self.__logger = get_logger(
                logger_name=__name__.split('.')[0],
                logger_version=__version__,
                logger_format=self.logger_format,
                logger_level=self.logger_level,
                logger_output=self.logger_output
            )

        return self.__logger

    def __init__(
        self,
        logger_level=logging.INFO,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR,
        timezone=None
    ):
        self.logger_level = logger_level
        self.logger_format = logger_format
        self.logger_output = logger_output

        if timezone is not None:
            self.timezone = timezone
        else:
            self.timezone = __TIMEZONE_NAME_DEFAULT__

        self.time_start = dt.datetime.now()

    @property
    def tmc_credentials(self):
        return self.__tmc_credentials

    @tmc_credentials.setter
    def tmc_credentials(self, value):
        self.__tmc_credentials = value

    @property
    def api_key(self):
        return None if self.tmc_credentials is None else self.tmc_credentials.get('api_key', None)

    @api_key.setter
    def api_key(self, value):
        if self.tmc_credentials is None:
            self.tmc_credentials = {}

        if 'api_key' in self.tmc_credentials:
            self.tmc_credentials.pop('api_key')

        self.tmc_credentials.update({'api_key': value})

    @property
    def session_token(self):
        return None if self.tmc_credentials is None \
            else self.tmc_credentials.get('session_token', None)

    @session_token.setter
    def session_token(self, value):
        if self.tmc_credentials is None:
            self.tmc_credentials = {}

        if 'session_token' in self.tmc_credentials:
            self.tmc_credentials.pop('session_token')

        self.tmc_credentials.update({'session_token': value})

    @property
    def timezone(self):
        """Get Property: timezone
        """
        return self.__timezone

    @timezone.setter
    def timezone(self, value):
        """Set Property: timezone
        """
        tz_name = value
        if not validate_tz_name(tz_name):
            raise ValueError("Invalid timezone name assigned: {}".format(tz_name))

        self.__timezone = tz_name

    __data = None

    @property
    def data(self):
        """Provide created reader populated with file data."""
        return self.__data

    @data.setter
    def data(self, value):
        """Provide data value."""
        self.__data = value

    def tune_mat_request_path(self, mat_api_version, controller, action):
        """TUNE Reporting API service path

        Args:
            mat_api_version:
            controller:
            action:

        Returns:

        """
        request_path = "{}/{}/{}/{}".format(self._TUNE_MANAGEMENT_API_ENDPOINT, mat_api_version, controller, action)

        return request_path

    def tune_v2_request_retry_func(self, response):
        """Request Retry Function

        Args:
            response:

        Returns:
            Boolean

        """
        try:
            response_json = response.json()
        except Exception as ex:
            # No JSON response available.
            raise TuneReportingError(
                error_message='Invalid JSON response: {}'.format(response.text),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_JSON_DECODING
            )

        self.logger.debug("TMC API V2: Check for Retry: Start", extra=response_json)

        tune_v2_status_code = None
        tune_v2_errors_messages = ""

        if 'status_code' in response_json:
            tune_v2_status_code = response_json['status_code']

        if 'errors' in response_json:
            tune_v2_errors = response_json['errors']
            if isinstance(tune_v2_errors, dict) \
                    and 'message' in tune_v2_errors:
                tune_v2_errors_messages += tune_v2_errors['message']
            elif isinstance(tune_v2_errors, list):
                for tune_v2_error in tune_v2_errors:
                    if isinstance(tune_v2_error, dict) \
                            and 'message' in tune_v2_error:
                        tune_v2_errors_messages += tune_v2_error['message']

        tune_v2_status_type = http_status_code_to_type(tune_v2_status_code)

        response_extra = {
            'status_code': tune_v2_status_code,
            'status_type': tune_v2_status_type,
        }

        if tune_v2_errors_messages:
            response_extra.update({'error_messages': safe_str(tune_v2_errors_messages)})

        self.logger.debug("TMC API Base: Check for Retry: Response", extra=response_extra)

        if tune_v2_status_code == 200:
            self.logger.debug("TMC API Base: Check for Retry: Success", extra=response_extra)
            return False

        if tune_v2_status_code in [401, 403]:
            self.logger.error("TMC API: Request: Error", extra={'status_code': tune_v2_status_code})
            raise TuneRequestError(
                error_message=tune_v2_errors_messages,
                error_code=tune_v2_status_code,
            )

        if tune_v2_status_code in [404, 500]:
            if "Api key was not found." in tune_v2_errors_messages:
                self.logger.error("TMC API: Request: Error", extra={'tune_v2_status_code': tune_v2_status_code})

                raise TuneRequestError(
                    error_message=tune_v2_errors_messages,
                    error_code=tune_v2_status_code,
                )

            self.logger.warning("TMC API Base: Check for Retry: Retry Candidate", extra=response_extra)
            return True

        self.logger.warning("TMC API Base: Check for Retry: No Retry", extra=response_extra)
        return False

    @property
    def generator(self):
        """Generate report data."""
        if not self.data or len(self.data) == 0:
            yield []
        else:
            for (i, item) in enumerate(self.data):
                yield item

    def tmc_auth(self, tmc_api_key):
        """TMC Authentication"""
        if not tmc_api_key:
            raise ValueError("Parameter 'tmc_api_key' not defined.")

        self.logger.info("TMC Authentication: Start")

        # Attempt to authenticate.
        request_url = ('https://api.mobileapptracking.com/v2/advertiser/find')

        request_params = {'api_key': tmc_api_key}

        auth_request_curl = command_line_request_curl_get(request_url=request_url, request_params=request_params)

        try:
            auth_response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_retry=None,
                request_retry_http_status_codes=None,
                request_retry_func=None,
                request_retry_excps_func=None,
                request_label="TMC Authentication"
            )
        except TuneRequestBaseError as tmc_ex:
            self.logger.error("TMC Authentication: Failed", extra=tmc_ex.to_dict())
            raise

        except Exception as ex:
            print_traceback(ex)
            self.logger.error("TMC Authentication: Failed: {}".format(get_exception_message(ex)))
            raise

        if auth_response.status_code != requests.codes.ok:
            raise TuneReportingError(
                error_message="Invalid request",
                error_request_curl=auth_request_curl,
                error_code=auth_response.status_code
            )

        try:
            decoded_resp = auth_response.json()
        except Exception as ex:
            # No JSON response available.
            raise TuneReportingError(
                error_message='Invalid JSON response: {}'.format(auth_response.text),
                errors=ex,
                error_request_curl=auth_request_curl,
                error_code=TuneReportingErrorCodes.REP_ERR_AUTH_JSON_ERROR
            )

        tmc_status_code = decoded_resp.get('status_code', None)
        tmc_errors = decoded_resp.get('errors', None)

        if tmc_errors:
            error_code = tmc_status_code
            errors = []
            if isinstance(tmc_errors, list):
                error_list = tmc_errors
                error_list = error_list if error_list else []
                for error in error_list:
                    error_message = error.get('message', None)
                    if error_message:
                        errors.append(error_message)
                        if error_message.startswith("Invalid api key"):
                            error_code = TuneReportingErrorCodes.UNAUTHORIZED

            elif isinstance(tmc_errors, dict):
                error_message = tmc_errors.get('message', None)
                if error_message:
                    errors.append(error_message)

            raise TuneReportingError(
                error_message="Error status: {}".format(tmc_errors),
                error_request_curl=auth_request_curl,
                error_code=error_code,
            )

        return decoded_resp
