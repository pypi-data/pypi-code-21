#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertiser Stats Abstract Base Class.
"""

import datetime as dt
import logging
import os
import time
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse
from pyhttpstatus_utils import (
    is_http_status_type,
    HttpStatusType,
)
from requests_mv_integrations.support import (validate_json_response)
from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from tune_reporting.errors import (
    print_traceback,
    get_exception_message,
    TuneReportingErrorCodes,
)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import python_check_version
from tune_reporting.readers.report_reader_json import (ReportReaderJSON)
from tune_reporting import (__python_required_version__)
from tune_reporting.readers.report_reader_csv import (ReportReaderCSV)
from tune_reporting.tmc.tune_mobileapptracking_api import (TuneMobileAppTrackingApi)
from tune_reporting.tmc.v2.management import (TuneV2AuthenticationTypes)
from tune_reporting.tmc.tmc_auth_v2_session_token import (tmc_auth_v2_session_token)
from logging_mv_integrations import (LoggingFormat, LoggingOutput)
from safe_cast import (
    safe_int,
    safe_dict,
)

python_check_version(__python_required_version__)


# @brief TUNE v3 Logs Actions ENUM
#
# @namespace tune_reporting.TuneV3LogsAdvertisersActions
class TuneV3LogsAdvertisersActions(object):
    """v3 Logs Actions
    """
    FIND = "find"
    EXPORT = "export"


# @brief TUNE Advertiser Stats Formats ENUM
#
# @namespace tune_reporting.TuneV3LogsAdvertisersLimitMax
class TuneV3LogsAdvertisersLimitMax(object):
    """Data formats for Advertiser Sites.
    """
    FIND = 5000
    EXPORT = 200000


# @brief TUNE Advertiser Stats Formats ENUM
#
# @namespace tune_reporting.TuneV3LogsAdvertisersResponseFormats
class TuneV3LogsAdvertisersResponseFormats(object):
    """Data formats for Advertiser Sites.
    """
    JSON = "json"
    CSV = "csv"


# @brief TUNE Advertiser Stats Abstract Base Class.
#
# @namespace tune_reporting.TuneV3LogsAdvertisersBase
class TuneV3LogsAdvertisersBase(TuneMobileAppTrackingApi):
    """TUNE Advertiser Stats Abstract Base Class.
    """

    __metaclass__ = ABCMeta

    _FILTER_NOT_DEBUG_NOR_TEST_DATA = (
        "(debug_mode = 0 OR debug_mode is NULL)"
        " AND "
        "(test_profile_id = 0 OR test_profile_id IS NULL)"
    )

    _CONTROLLER = "logs/advertisers/{advertiser_id}"

    # Initialize Job
    #
    def __init__(
        self,
        logs_advertisers_type,
        timezone=None,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR
    ):
        """Initialize TUNE Advertiser Stats Abstract Base Class.
        """
        super(TuneV3LogsAdvertisersBase, self).__init__(
            timezone=timezone,
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

        self.controller = None
        self.logs_advertisers_type = logs_advertisers_type

    # Collect data: TUNE Advertiser Stats Actuals.
    #
    def collect(
        self,
        auth_value,
        auth_type,
        auth_type_use,
        start_date,
        end_date,
        advertiser_id,
        request_params=None,
        request_retry=None,
        request_action=TuneV3LogsAdvertisersActions.FIND
    ):
        """Collect data: TUNE Advertiser Stats Actuals.

        Args:
            tmc_api_key:
            start_date:
            end_date:
            advertiser_id:
            request_params:
            request_retry:
            request_action:

        Returns:

        """
        if not auth_value:
            raise ValueError("TMC v3 Logs Advertisers Base: Collect: Value 'auth_value' not provided.")
        if not auth_type:
            raise ValueError("TMC v3 Logs Advertisers Base: Collect: Value 'auth_type' not valid.")
        if not auth_type_use or \
                not TuneV2AuthenticationTypes.validate(auth_type_use):
            raise ValueError("TMC v3 Logs Advertisers Base: Collect: Value 'auth_type_use' not valid.")
        if not advertiser_id:
            raise ValueError("TMC v3 Logs Advertisers Base: Collect: Value 'advertiser_id' not valid.")

        if auth_type == TuneV2AuthenticationTypes.API_KEY:
            self.api_key = auth_value

            if auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
                self.session_token = tmc_auth_v2_session_token(
                    tmc_api_key=self.api_key,
                    logger_level=self.logger_level,
                    logger_format=self.logger_format,

                )
        elif auth_type == TuneV2AuthenticationTypes.SESSION_TOKEN:
            self.session_token = auth_value
        else:
            raise ValueError(error_message="Invalid 'auth_type': '{}'".format(auth_type))

        auth_value_use = None
        if auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
            if self.session_token is None:
                raise TuneReportingError(
                    error_message="Value 'session_token' not defined.",
                    error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
                )

            auth_value_use = self.session_token

        elif auth_type_use == TuneV2AuthenticationTypes.API_KEY:
            if self.api_key is None:
                raise TuneReportingError(
                    error_message="Value 'api_key' not defined.",
                    error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE,
                )

            auth_value_use = self.api_key

        if not auth_value_use:
            raise TuneReportingError(
                error_message="Value 'auth_value_use' not defined.",
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE,
            )

        self.advertiser_id = advertiser_id

        self.controller = self._CONTROLLER.format(advertiser_id=self.advertiser_id)

        self._collect(auth_type_use, start_date, end_date, request_params, request_retry, request_action)

    @abstractmethod
    def _collect(
        self,
        auth_type_use,
        start_date,
        end_date,
        request_params=None,
        request_retry=None,
        request_action=TuneV3LogsAdvertisersActions.FIND
    ):
        """Collect data: TUNE Advertiser Stats.

        Args:
            start_date:
            end_date:
            request_params:
            request_retry:
            request_action:

        Returns:

        """

        raise NotImplementedError

    def _find_v3(self, request_params, request_retry=None, request_label="TMC v3 Logs Advertisers"):
        """Gather data using action 'find'

        Args:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.debug(("TMC v3 Logs Advertisers Base: "
                           "Logs '{}': "
                           "Action 'find'").format(self.logs_advertisers_type))

        if "start_date" not in request_params:
            raise ValueError("Missing attribute 'start_date' in parameter 'request_params'")
        request_start_date = request_params["start_date"]

        if "end_date" not in request_params:
            raise ValueError("Missing attribute 'end_date' in parameter 'request_params'")
        request_end_date = request_params["end_date"]

        datetime_start = dt.datetime.strptime(request_start_date, '%Y-%m-%d')
        datetime_end = dt.datetime.strptime(request_end_date, '%Y-%m-%d')

        str_date_start = str(datetime_start.date())
        str_date_end = str(datetime_end.date())

        self.logger.debug(
            "TMC v3 Logs Advertisers Base: Action 'find'",
            extra={'start_date': str_date_start,
                   'end_date': str_date_end}
        )

        if not request_retry:
            request_retry = {'timeout': 600}

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v3",
                controller=self.controller,
                action=self.logs_advertisers_type
            )

        if 'response_format' not in request_params:
            request_params['response_format'] = \
                TuneV3LogsAdvertisersResponseFormats.JSON

        request_params["start_date"] += "T00:00:00Z"
        request_params["end_date"] += "T23:59:59Z"

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_retry=None,
                request_retry_http_status_codes=None,
                request_retry_func=None,
                request_retry_excps_func=None,
                request_label=request_label
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Base: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Base: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TMC v3 Logs Advertisers Base: {}".format(get_exception_message(ex)))
            raise

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v3 Logs Advertisers: Action 'find'",
        )

        data = json_response['data']

        self.data = data

    def _export_v3_download_csv(self, request_params, request_retry=None):
        """Export and then Read download CSV

        Args:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.debug(("TMC v3 Logs Advertisers Base: "
                           "Logs '{}': "
                           "Action 'exports'").format(self.logs_advertisers_type))

        data = []

        delta_day = dt.timedelta(days=1)

        if "start_date" not in request_params:
            raise ValueError("Missing attribute 'start_date' in parameter 'request_params'")
        request_start_date = request_params["start_date"]

        if "end_date" not in request_params:
            raise ValueError("Missing attribute 'end_date' in parameter 'request_params'")
        request_end_date = request_params["end_date"]

        datetime_start = dt.datetime.strptime(request_start_date, '%Y-%m-%d')
        datetime_end = dt.datetime.strptime(request_end_date, '%Y-%m-%d')

        str_date_start = str(datetime_start.date())
        str_date_end = str(datetime_end.date())

        self.logger.debug(
            msg=("TuneV3LogsAdvertisersBase"),
            extra={'action': 'export',
                   'start_date': str_date_start,
                   'end_date': str_date_end}
        )

        next_end_date = datetime_start - delta_day

        done = False

        export_jobs = []

        while not done:
            next_start_date = next_end_date + delta_day
            next_end_date = next_end_date + delta_day

            if next_end_date > datetime_end:
                next_end_date = datetime_end

            if next_end_date == datetime_end:
                done = True

            # pylint: disable=no-member
            next_start_date_yyyy_mm_dd = \
                next_start_date.strftime('%Y-%m-%d')

            next_end_date_yyyy_mm_dd = \
                next_end_date.strftime('%Y-%m-%d')
            # pylint: enable=no-member

            next_start_date_yyyy_mm_dd += "T00:00:00Z"
            next_end_date_yyyy_mm_dd += "T23:59:59Z"

            request_params["start_date"] = \
                next_start_date_yyyy_mm_dd
            request_params["end_date"] = \
                next_end_date_yyyy_mm_dd

            export_job = self._export_v3_job_to_queue(request_params, request_retry)

            self.logger.debug(
                "TuneV3LogsAdvertisersBase",
                extra={
                    'action': 'export',
                    'start_date': next_start_date_yyyy_mm_dd,
                    'end_date': next_end_date_yyyy_mm_dd,
                    'job': export_job
                }
            )

            export_jobs.append({
                'job_handle': export_job,
                'start_date': next_start_date_yyyy_mm_dd,
                'end_date': next_end_date_yyyy_mm_dd
            })

        self.logger.debug("TuneV3LogsAdvertisersBase", extra={'action': 'export', 'export_job_count': len(export_jobs)})

        jobs_total_count = 0

        for export_job in export_jobs:
            export_job_handle = export_job['job_handle']
            export_job_start_date = export_job['start_date']
            export_job_end_date = export_job['end_date']

            report_url = self._check_v3_job_status_on_queue(export_job_handle, request_retry=request_retry)

            generator_data_stats = self._read_stats_data(export_job_handle, report_url)

            job_row_count = 0

            for row in list(generator_data_stats):
                if len(row) == 0:
                    continue
                job_row_count += 1
                data.append(row)

            jobs_total_count += job_row_count

            self.logger.debug(
                msg=("TuneV3LogsAdvertisersBase"),
                extra={
                    'action': 'export',
                    'start_date': export_job_start_date,
                    'end_date': export_job_end_date,
                    'job_handle': export_job_handle,
                    'job_row_count': job_row_count
                }
            )

        self.logger.debug(
            msg=("TuneV3LogsAdvertisersBase"),
            extra={'action': 'export',
                   'total_data_count': len(data),
                   'total_job_sum_count': jobs_total_count}
        )

        self.data = data

    def _export_v3_job_to_queue(self, request_params, request_retry=None, request_label="TMC v3 Job On Queue"):
        """Gather data using action export.json.

        :param request_params:
        :param request_retry:
        :return:
        """

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v3",
                controller=self.controller,
                action="exports/{}".format(
                    self.logs_advertisers_type
                )
            )

        self.logger.debug(
            msg=("TMC v3 Logs Advertisers Base: "
                 "Logs '{}': "
                 "Action 'exports': "
                 "Start Advertiser Report Actuals").format(self.logs_advertisers_type),
            extra={'start_date': request_params["start_date"],
                   'end_date': request_params["end_date"]}
        )

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_retry=request_retry,
                request_retry_http_status_codes=None,
                request_retry_func=self.tune_v3_request_retry_func,
                request_retry_excps_func=None,
                request_label=request_label
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Base: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Base: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TMC v3 Logs Advertisers Base: {}".format(get_exception_message(ex)))
            raise

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v3 Logs Advertisers: '{}': Action 'exports'".format(self.logs_advertisers_type)
        )

        if ('handle' not in json_response or not json_response['handle']):
            raise TuneReportingError(
                error_message=(
                    "TMC v3 Logs Advertisers Base: "
                    "Logs '{}': "
                    "Action 'exports': "
                    "Response missing 'handle': {}"
                ).format(self.logs_advertisers_type, str(json_response)),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )

        export_job = json_response['handle']

        if not export_job:
            raise TuneReportingError(
                error_message=(
                    "TMC v3 Logs Advertisers Base: "
                    "Logs '{}': "
                    "Action 'exports': "
                    "Response missing 'handle'"
                ).format(self.logs_advertisers_type),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )

        self.logger.info(
            "TuneV3LogsAdvertisersBase",
            extra={
                'advertiser_type': self.logs_advertisers_type,
                'action': 'exports',
                'start_date': request_params["start_date"],
                'end_date': request_params["end_date"],
                'job': export_job
            }
        )

        return export_job

    def _check_v3_job_status_on_queue(self, export_job, request_retry=None, request_label="TMC v3 Job Status On Queue"):
        """Status of Export Report.

        Args:
            export_job:
            request_retry:

        Returns:

        """
        request_label = "v3 Logs Advertisers Check Export Status"

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v3",
                controller=self.controller,
                action="exports/{}".format(
                    export_job
                )
            )

        self.logger.info((
            "TMC v3 Logs Advertisers Base: Check Export Status: "
            "Logs '{}': "
            "Action: 'exports status', "
            "Status of Export Report for "
            "Job Handle: '{}'"
        ).format(self.logs_advertisers_type, export_job))

        tries = -1  # default: -1 (indefinite)
        delay = 10
        jitter = 0
        max_delay = 60

        if request_retry:
            if 'delay' in request_retry:
                delay = request_retry['delay']
            if 'jitter' in request_retry:
                jitter = request_retry['jitter']
            if 'max_delay' in request_retry:
                max_delay = request_retry['max_delay']

        request_params = {"session_token": self.session_token}

        self.logger.debug("TMC v3 Logs Advertisers Base: Check Export Status", extra={'request_url': request_url})

        self.logger.debug(
            "TMC v3 Logs Advertisers Base: Check Export Status: Request Retry",
            extra={'tries': tries,
                   'delay': delay,
                   'jitter': jitter,
                   'max_delay': max_delay}
        )

        self.logger.debug(
            "TMC v3 Logs Advertisers Base: Check Export Status: Request",
            extra={'request_params': safe_dict(request_params)}
        )

        report_url = None
        _attempts = 1
        export_percent_complete = 0

        export_status_action = 'exports status'

        self.logger.warning(
            "TMC v3 Logs Advertisers Base: Check Export Status",
            extra={'job': export_job,
                   'attempt': _attempts,
                   'action': export_status_action}
        )

        time.sleep(10)

        _tries, _delay = tries, delay
        while True:
            try:
                response = self.mv_request.request(
                    request_method="GET",
                    request_url=request_url,
                    request_params=request_params,
                    request_retry=None,
                    request_retry_http_status_codes=None,
                    request_retry_func=self.tune_v3_request_retry_func,
                    request_retry_excps_func=None,
                    request_label=request_label
                )

            except TuneRequestBaseError as tmc_req_ex:
                self.logger.error(
                    "TMC v3 Logs Advertisers Base: Check Export Status: Failed",
                    extra=tmc_req_ex.to_dict(),
                )
                raise

            except TuneReportingError as tmc_rep_ex:
                self.logger.error(
                    "TMC v3 Logs Advertisers Base: Check Export Status: Failed",
                    extra=tmc_rep_ex.to_dict(),
                )
                raise

            except Exception as ex:
                print_traceback(ex)

                self.logger.error(
                    "TMC v3 Logs Advertisers Base: Check Export Status: Failed",
                    extra={'error': get_exception_message(ex)}
                )
                raise

            http_status_successful = is_http_status_type(
                http_status_code=response.status_code, http_status_type=HttpStatusType.SUCCESSFUL
            )

            if not http_status_successful:
                raise TuneReportingError(
                    error_message="Failed to get export status on queue: {}".format(response.status_code),
                    error_code=TuneReportingErrorCodes.REP_ERR_REQUEST
                )

            json_response = response.json()

            export_percent_complete = 0
            if "percent_complete" in json_response:
                export_percent_complete = \
                    safe_int(json_response["percent_complete"])

            self.logger.info(
                "TMC v3 Logs Advertisers Base: Check Job Export Status",
                extra={
                    'job': export_job,
                    'response_status_code': json_response["status"],
                    'export_percent_complete': safe_int(export_percent_complete)
                }
            )

            if (export_percent_complete == 100 and json_response["status"] == "complete" and json_response["url"]):
                report_url = json_response["url"]

                self.logger.info(
                    "TMC v3 Logs Advertisers Base: Check Job Export Status: Completed",
                    extra={
                        'job': export_job,
                        'report_url': report_url,
                        'request_label': request_label,
                        'export_percent_complete': safe_int(export_percent_complete)
                    }
                )

                break

            if tries >= 0:
                _tries -= 1
                if _tries == 0:
                    self.logger.error(("TMC v3 Logs Advertisers Base: "
                                       "Check Job Export Status: Exhausted Retries"),
                                      extra={
                                          'attempt': _attempts,
                                          'tries': _tries,
                                          'action': export_status_action,
                                          'request_label': request_label,
                                          'export_percent_complete': export_percent_complete
                                      })

                    raise TuneReportingError(
                        error_message=(
                            "TMC v3 Logs Advertisers Base: "
                            "Check Job Export Status: "
                            "Exhausted Retries: "
                            "Percent Completed: {}"
                        ).format(export_percent_complete),
                        error_code=TuneReportingErrorCodes.REP_ERR_JOB_STOPPED
                    )

            _attempts += 1

            self.logger.warning(
                "TMC v3 Logs Advertisers Base: Check Export Status",
                extra={'attempt': _attempts,
                       'job': export_job,
                       'delay': _delay,
                       'action': 'exports status'}
            )
            time.sleep(_delay)

            _delay += jitter
            _delay = min(_delay, max_delay)

        if export_percent_complete == 100 and not report_url:
            raise TuneReportingError(
                error_message=(
                    "TMC v3 Logs Advertisers Base: Check Job Export Status: "
                    "Download report URL: Undefined"
                )
            )

        self.logger.info(
            "TMC v3 Logs Advertisers Base: Check Job Export Status: Finished",
            extra={
                'attempt': _attempts,
                'action': export_status_action,
                'report_url': report_url,
                'request_label': request_label,
                'export_percent_complete': export_percent_complete,
                'job': export_job
            }
        )

        return report_url

    def _read_stats_data(self, export_job_handle, report_url, report_format=None):
        if not export_job_handle:
            raise ValueError("Argument 'export_job_handle' not assigned.")
        if not report_url:
            raise ValueError("Argument 'report_url' not assigned.")

        self.logger.info(("TMC v3 Logs Advertisers Base: "
                          "Start Advertiser Report Stats read: "
                          "Job Handle: '{}'").format(export_job_handle))

        if not report_format:
            path = urlparse(report_url).path
            ext = os.path.splitext(path)[1]
            report_format = ext[1:]

        self.logger.info(("TMC v3 Logs Advertisers Base: "
                          "Reading URL '{}' with format '{}'").format(report_url, report_format))

        # pylint: disable=redefined-variable-type
        if report_format == TuneV3LogsAdvertisersResponseFormats.JSON:
            report_reader = ReportReaderJSON(report_url)
        elif report_format == TuneV3LogsAdvertisersResponseFormats.CSV:
            report_reader = ReportReaderCSV(report_url)
        else:
            raise TuneReportingError(error_message="Unexpected report format: '{}'".format(report_format))
        # pylint: enable=redefined-variable-type

        if not report_reader:
            raise TuneReportingError(error_message="Report reader not created for format {}".format(report_format))

        report_reader.read()

        self.logger.info(("TMC v3 Logs Advertisers Base: " "Finished Advertiser Report Stats read"))

        return report_reader.generator

    def tune_v3_request_retry_func(self, response):
        """Request Retry Function

        Args:
            response:

        Returns:
            Boolean

        """
        response_json = response.json()

        self.logger.debug("Check for Retry", extra={'response': response_json})

        tune_v2_errors = None
        tune_v2_errors_error_code = None
        tune_v2_errors_message = None

        if 'errors' in response_json:
            tune_v2_errors = response_json['errors']
            tune_v2_errors_error_code = tune_v2_errors[0]['error_code']
            tune_v2_errors_message = tune_v2_errors[0]['message']

        self.logger.debug(
            "Check for Retry: Response: Status: {}, Errors: '{}'".
            format(tune_v2_errors_error_code, tune_v2_errors_message)
        )

        if tune_v2_errors is None:
            return False

        # For V3, it is not clear what would be a retry status.
        return False
