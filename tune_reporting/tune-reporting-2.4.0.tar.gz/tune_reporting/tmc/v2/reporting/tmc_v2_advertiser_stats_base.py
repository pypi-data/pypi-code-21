#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertiser Stats Abstract Base Class.
"""

import logging
import datetime as dt
import ujson as json
import os
import time
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse

from pyhttpstatus_utils import (
    HttpStatusType,
    HttpStatusCode,
    is_http_status_type,
)
from requests_mv_integrations.support import (validate_json_response)
from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from tune_reporting.errors import (print_traceback, get_exception_message, TuneReportingErrorCodes)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import (python_check_version)
from tune_reporting.readers.report_reader_json import (ReportReaderJSON)
from tune_reporting import (__python_required_version__)
from tune_reporting.readers.report_reader_csv import (ReportReaderCSV)
from tune_reporting.tmc.v2.management import (TuneV2AuthenticationTypes)
from tune_reporting.tmc.tmc_auth_v2_session_token import (tmc_auth_v2_session_token)
from tune_reporting.tmc.tune_mobileapptracking_api import (TuneMobileAppTrackingApi)
from logging_mv_integrations import (LoggingFormat, LoggingOutput)
from safe_cast import (
    safe_dict,
    safe_int,
)
python_check_version(__python_required_version__)


# @brief TUNE Advertiser Stats Actions ENUM
#
# @namespace tune_reporting.TuneV2AdvertiserStatsExportActions
class TuneV2AdvertiserStatsActions(object):
    """Status states for Advertiser Sites.
    """
    FIND = "find"
    EXPORT = "export"


# @brief TUNE Advertiser Stats Export Actions ENUM
#
# @namespace tune_reporting.TuneV2AdvertiserStatsExportActions
class TuneV2AdvertiserStatsExportActions(object):
    """Export actions for Advertiser Sites.
    """
    EXPORT = "export"
    FIND_EXPORT_QUEUE = "find_export_queue"


# @brief TUNE Advertiser Stats Status Actions ENUM
#
# @namespace tune_reporting.TuneV2AdvertiserStatsStatusAction
class TuneV2AdvertiserStatsStatusAction(object):
    """Export Status actions for Advertiser Sites.
    """
    STATUS = "status"
    DOWNLOAD = "download"


# @brief TUNE Advertiser Stats Formats ENUM
#
# @namespace tune_reporting.TuneV2AdvertiserStatsFormats
class TuneV2AdvertiserStatsFormats(object):
    """Data formats for Advertiser Sites.
    """
    JSON = "json"
    CSV = "csv"


# @brief TUNE Advertiser Stats Abstract Base Class.
#
# @namespace tune_reporting.TuneV2AdvertiserStatsBase
class TuneV2AdvertiserStatsBase(TuneMobileAppTrackingApi):
    """TUNE Advertiser Stats Abstract Base Class.
    """

    __metaclass__ = ABCMeta

    _FILTER_NOT_DEBUG_NOR_TEST_DATA = (
        "(debug_mode = 0 OR debug_mode is NULL)"
        " AND "
        "(test_profile_id = 0 OR test_profile_id IS NULL)"
    )

    _TUNE_ADVERTISING_STATS_TPL = \
        "tmc_advertising_stats_{job_id}.{format}"

    # Initialize Job
    #
    def __init__(
        self,
        controller,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR,
        timezone=None
    ):
        """Initialize TUNE Advertiser Stats Abstract Base Class.
        """
        super(TuneV2AdvertiserStatsBase, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output,
            timezone=timezone
        )

        self.controller = controller

    # Collect data: TUNE Advertiser Stats Actuals.
    #
    def collect(
        self,
        auth_value,
        auth_type,
        auth_type_use,
        start_date,
        end_date,
        request_params=None,
        request_retry=None,
        request_action=TuneV2AdvertiserStatsActions.FIND
    ):
        """Collect data: TUNE Advertiser Stats Base

        Args:
            auth_value:
            auth_type:
            start_date:
            end_date:
            request_params:
            request_retry:
            request_action:

        Returns:

        """
        self.logger.info("TMC v2 Advertiser Stats: Collect: {}".format(request_action))

        if not auth_value:
            raise ValueError(error_message="TMC v2 Advertiser Stats: Collect: Value 'auth_value' not provided.")
        if not auth_type or \
                not TuneV2AuthenticationTypes.validate(auth_type):
            raise ValueError(error_message="TMC v2 Advertiser Stats: Collect: Value 'auth_type' not valid.")
        if not auth_type_use or \
                not TuneV2AuthenticationTypes.validate(auth_type_use):
            raise ValueError(error_message="TMC v2 Advertiser Stats: Collect: Value 'auth_type_use' not valid.")

        if auth_type == TuneV2AuthenticationTypes.API_KEY:
            self.api_key = auth_value

            if auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
                self.session_token = tmc_auth_v2_session_token(
                    tmc_api_key=self.api_key, logger_level=self.logger_level, logger_format=self.logger_format
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
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        self._collect(auth_type_use, start_date, end_date, request_params, request_retry, request_action)

    # Stream data: TUNE Advertiser Stats Base
    #
    def stream(
        self,
        auth_value,
        auth_type,
        auth_type_use,
        start_date,
        end_date,
        request_params,
        request_retry=None,
    ):
        """Stream data: TUNE Advertiser Stats Base

        Args:
            auth_value:
            auth_type:
            start_date:
            end_date:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.info("TMC v2 Advertiser Stats: Stream")

        if not auth_value:
            raise ValueError(error_message="TMC v2 Advertiser Stats: Stream: Value 'auth_value' not provided.")
        if not auth_type or \
                not TuneV2AuthenticationTypes.validate(auth_type):
            raise ValueError(error_message="TMC v2 Advertiser Stats: Stream: Value 'auth_type' not valid.")
        if not auth_type_use or \
                not TuneV2AuthenticationTypes.validate(auth_type_use):
            raise ValueError(error_message="TMC v2 Advertiser Stats: Stream: Value 'auth_type_use' not valid.")

        if not request_params:
            raise ValueError(error_message="Value 'request_params' not provided.")

        if auth_type == TuneV2AuthenticationTypes.API_KEY:
            self.api_key = auth_value

            if auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
                self.session_token = tmc_auth_v2_session_token(
                    tmc_api_key=self.api_key, logger_level=self.logger_level, logger_format=self.logger_format
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
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        return self._stream_v2(
            auth_type_use=auth_type_use,
            start_date=start_date,
            end_date=end_date,
            request_params=request_params,
            request_retry=request_retry
        )

    @abstractmethod
    def _collect(
        self,
        auth_type_use,
        start_date,
        end_date,
        request_params=None,
        request_retry=None,
        request_action=TuneV2AdvertiserStatsActions.FIND,
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

    @abstractmethod
    def _stream_v2(
        self,
        auth_type_use,
        start_date,
        end_date,
        request_params,
        request_retry=None,
    ):
        """Collect data: TUNE Advertiser Stats.

        Args:
            start_date:
            end_date:
            request_params:
            request_retry:

        Returns:

        """

        raise NotImplementedError

    def _find_v2(
        self,
        request_params,
        request_retry=None,
        request_label="TMC v2 Advertiser Stats Find",
    ):
        """Gather data using action find.json.
        """

        self.logger.debug("TuneV2AdvertiserStatsBase", extra={'action': 'find'})

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

        self.logger.debug(("TuneV2AdvertiserStatsBase"),
                          extra={'action': 'find',
                                 'start_date': str_date_start,
                                 'end_date': str_date_end})

        if not request_retry:
            request_retry = {'timeout': 60}

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller=self.controller,
                action="find"
            )

        if 'format' not in request_params:
            request_params['format'] = TuneV2AdvertiserStatsFormats.JSON

        request_params["start_date"] += " 00:00:00"
        request_params["end_date"] += " 23:59:59"

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_label=request_label
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v2 Advertiser Stats: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v2 Advertiser Stats: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TMC v2 Advertiser Stats: {}".format(get_exception_message(ex)))
            raise

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v2 Advertiser Stats: Action 'find'"
        )

        if json_response['status_code'] != 200:
            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: "
                               "Action 'find': "
                               "Failed to find stats: {}, {}").format(
                                   json_response['status_code'],
                                   json.dumps(json_response),
                               ),
                error_code=TuneReportingErrorCodes.REP_ERR_REQUEST
            )

        data = json_response['data']
        self.data = data

    def _export_v2_download_csv(
        self,
        tmp_directory,
        auth_type_use,
        export_controller,
        export_action,
        export_status_controller,
        export_status_action,
        request_params,
        request_retry=None,
    ):
        """Gather Export by Downloading CSV and reading Data

        Args:
            export_controller:
            export_action:
            export_status_controller:
            export_status_action:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.debug(("TMC v2 Advertiser Stats: Export CSV Download: "
                           "Actions '{}' and '{}'").format(export_action, export_status_action))

        if not request_params:
            raise ValueError("Missing parameter 'request_params'")

        if "start_date" not in request_params:
            raise ValueError("Missing attribute 'start_date' in parameter 'request_params'")
        request_start_date = request_params["start_date"]

        if "end_date" not in request_params:
            raise ValueError("Missing attribute 'end_date' in parameter 'request_params'")
        request_end_date = request_params["end_date"]

        if 'format' not in request_params:
            request_params['format'] = TuneV2AdvertiserStatsFormats.CSV
        export_format = request_params['format']

        datetime_start = dt.datetime.strptime(request_start_date, '%Y-%m-%d')
        datetime_end = dt.datetime.strptime(request_end_date, '%Y-%m-%d')

        str_date_start = str(datetime_start.date())
        str_date_end = str(datetime_end.date())

        self.logger.debug(("TMC v2 Advertiser Stats: Export CSV Download"),
                          extra={
                              'action': 'export',
                              'start_date': str_date_start,
                              'end_date': str_date_end,
                              'export_format': export_format
                          })

        data = []

        data, job_row_count = self._process_export_download_csv_v2(
            tmp_directory,
            data,
            auth_type_use,
            str_date_start,
            str_date_end,
            export_controller,
            export_action,
            export_status_controller,
            export_status_action,
            request_params,
            request_retry,
        )

        self.data = data

    def _export_stream_v2(
        self,
        auth_type_use,
        export_controller,
        export_action,
        export_status_controller,
        export_status_action,
        request_params,
        request_retry=None,
    ):
        """Gather Export using Requests Stream

        Args:
            export_controller:
            export_action:
            export_status_controller:
            export_status_action:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.debug(
            "TMC v2 Advertiser Stats: Gather Export by Requests Stream",
            extra={
                'export_action': export_action,
                'export_status_action': export_status_action,
                'request_retry': request_retry
            }
        )

        if not request_params:
            raise ValueError("Missing parameter 'request_params'")

        if "start_date" not in request_params:
            raise ValueError("Missing attribute 'start_date' in parameter 'request_params'")
        request_start_date = request_params["start_date"]

        if "end_date" not in request_params:
            raise ValueError("Missing attribute 'end_date' in parameter 'request_params'")
        request_end_date = request_params["end_date"]

        if 'format' not in request_params:
            request_params['format'] = TuneV2AdvertiserStatsFormats.CSV
        export_format = request_params['format']

        datetime_start = dt.datetime.strptime(request_start_date, '%Y-%m-%d')
        datetime_end = dt.datetime.strptime(request_end_date, '%Y-%m-%d')

        str_date_start = str(datetime_start.date())
        str_date_end = str(datetime_end.date())

        self.logger.debug(
            "TMC v2 Advertiser Stats: Gather Export by Requests Stream",
            extra={
                'action': 'export',
                'start_date': str_date_start,
                'end_date': str_date_end,
                'export_format': export_format,
                'request_retry': request_retry
            }
        )

        return self._process_export_stream_v2(
            auth_type_use,
            str_date_start,
            str_date_end,
            export_controller,
            export_action,
            export_status_controller,
            export_status_action,
            request_params,
            request_retry,
        )

    def _process_export_download_csv_v2(
        self,
        tmp_directory,
        data,
        auth_type_use,
        str_date_start,
        str_date_end,
        export_controller,
        export_action,
        export_status_controller,
        export_status_action,
        request_params,
        request_retry,
    ):
        """Process Export Job by Reading Downloaded CSV

        Args:
            data:
            str_date_start:
            str_date_end:
            export_controller:
            export_action:
            export_status_controller:
            export_status_action:
            request_params:
            request_retry:

        Returns:

        """
        auth_value = None
        if auth_type_use == TuneV2AuthenticationTypes.API_KEY:
            auth_value = self.api_key
        elif auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
            auth_value = self.session_token

        str_date_start += " 00:00:00"
        str_date_end += " 23:59:59"

        request_params["start_date"] = \
            str_date_start
        request_params["end_date"] = \
            str_date_end

        export_job_id = self._export_v2_job_to_queue(
            export_controller,
            export_action,
            request_params,
            request_retry,
        )

        export_report_url = self._check_v2_job_status_on_queue(
            auth_type_use,
            auth_value,
            export_status_controller,
            export_status_action,
            export_job_id,
            request_retry=request_retry,
        )

        if not export_report_url:
            raise TuneReportingError(
                error_message="Export URL not defined",
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE,
            )

        self.logger.info("TuneV2AdvertiserStatsBase", extra={'job_id': export_job_id, 'report_url': export_report_url})

        tmp_csv_file_name = self._TUNE_ADVERTISING_STATS_TPL.format(
            job_id=export_job_id, format=TuneV2AdvertiserStatsFormats.CSV
        )

        tmp_csv_file_name = tmp_csv_file_name.replace('-', '_')

        job_row_count = 0

        for row in self.mv_request.request_csv_download(
            tmp_csv_file_name=tmp_csv_file_name,
            tmp_directory=tmp_directory,
            request_method="GET",
            request_url=export_report_url,
            request_label="TMC v2 Advertiser Stats: Export: Download CSV"
        ):
            # for row in list(generator_data_stats):
            if len(row) == 0:
                continue

            job_row_count += 1
            data.append(row)

        if os.path.exists(tmp_csv_file_name):
            os.remove(tmp_csv_file_name)

        self.logger.debug(
            "TMC v2 Advertiser Stats: Process Export Job by Reading Downloaded CSV",
            extra={
                'action': 'export',
                'start_date': str_date_start,
                'end_date': str_date_end,
                'job_id': export_job_id,
                'row_count': job_row_count
            }
        )

        return (data, job_row_count)

    def _process_export_stream_v2(
        self,
        auth_type_use,
        str_date_start,
        str_date_end,
        export_controller,
        export_action,
        export_status_controller,
        export_status_action,
        request_params,
        request_retry,
        request_label="TMC v2 Advertiser Stats Export Stream",
    ):
        """Process Export Job by Steaming

        Args:
            str_date_start:
            str_date_end:
            export_controller:
            export_action:
            export_status_controller:
            export_status_action:
            request_params:
            request_retry:

        Returns:

        """
        auth_value = None
        if auth_type_use == TuneV2AuthenticationTypes.API_KEY:
            auth_value = self.api_key
        elif auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
            auth_value = self.session_token

        str_date_start += " 00:00:00"
        str_date_end += " 23:59:59"

        request_params["start_date"] = \
            str_date_start
        request_params["end_date"] = \
            str_date_end

        self.logger.debug(
            "TMC v2 Advertiser Stats: Export Stream V2: Export Job to Queue",
            extra={
                'controller': export_controller,
                'action': export_action,
                'request_params': safe_dict(request_params),
                'request_retry': safe_dict(request_retry)
            }
        )

        export_job_id = self._export_v2_job_to_queue(
            export_controller,
            export_action,
            request_params,
            request_retry,
        )

        self.logger.debug(
            "TMC v2 Advertiser Stats: Export Stream V2: Check Job status on Queue",
            extra={'controller': export_status_controller,
                   'action': export_status_action,
                   'job_id': export_job_id}
        )

        export_report_url = self._check_v2_job_status_on_queue(
            auth_type_use,
            auth_value,
            export_status_controller,
            export_status_action,
            export_job_id,
            request_retry=request_retry
        )

        if not export_report_url:
            raise TuneReportingError(
                error_message="Export URL not defined",
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE,
            )

        self.logger.info(("TMC v2 Advertiser Stats: "
                          "Export Stream V2: Request Completed Job"),
                         extra={'job_id': export_job_id,
                                'report_url': export_report_url})

        response = self.mv_request.request(
            request_method="GET", request_url=export_report_url, stream=True, request_label=request_label
        )

        self.logger.info(
            "TMC v2 Advertiser Stats: Export Stream V2: Response Completed Job",
            extra={
                'response_status_code': response.status_code,
                'response_headers': response.headers,
                'job_id': export_job_id,
                'report_url': export_report_url
            }
        )

        return response

    def _export_v2_job_to_queue(
        self,
        export_controller,
        export_action,
        request_params,
        request_retry=None,
        request_label="TMC v2 Job To Queue",
    ):
        """Export Report Request to Job Queue

        Args:
            export_controller:
            export_action:
            request_params:
            request_retry:

        Returns:
            Export Job ID

        """
        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller=export_controller,
                action=export_action
            )

        self.logger.debug(("TMC v2 Advertiser Stats: "
                           "Start Advertiser Report Actuals"),
                          extra={
                              'action': export_action,
                              'start_date': request_params["start_date"],
                              'end_date': request_params["end_date"]
                          })

        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=request_params,
                request_label=request_label,
                request_retry_func=self.tune_v2_request_retry_func
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v2 Advertiser Stats: Request Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v2 Advertiser Stats: Reporting Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error(get_exception_message(ex))

            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: Unexpected Failed: {}").format(get_exception_message(ex)),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        json_response = validate_json_response(
            response,
            request_curl=self.mv_request.built_request_curl,
            request_label="TMC v2 Advertiser Stats: Action '{}'".format(export_action)
        )

        if hasattr(response, 'url'):
            self.logger.info("TMC v2 Advertiser Stats: Reporting API: Export URL", extra={'response_url': response.url})

        if (not json_response or json_response['status_code'] != 200 or 'errors' in json_response):
            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: "
                               "Action '{}': "
                               "Failed to export stats: {}, {}").format(
                                   export_action, json_response['status_code'], json_response['errors']
                               ),
                error_code=TuneReportingErrorCodes.REP_ERR_REQUEST
            )

        if ('data' not in json_response or not json_response['data']):
            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: "
                               "Action '{}': "
                               "Missing data").format(export_action),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )
        json_data = json_response['data']

        export_job_id = None
        if export_action == TuneV2AdvertiserStatsExportActions.EXPORT:
            if ('job_id' not in json_data or not json_data['job_id']):
                raise TuneReportingError(
                    error_message=("TMC v2 Advertiser Stats: "
                                   "Action '{}': "
                                   "Response missing 'export_job_id': {}").format(export_action, str(json_data)),
                    error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
                )

            export_job_id = json_data['job_id']
        elif export_action == TuneV2AdvertiserStatsExportActions.FIND_EXPORT_QUEUE:
            export_job_id = json_data

        if not export_job_id:
            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: "
                               "Action '{}': "
                               "Response missing 'job_id'").format(export_action),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )

        self.logger.info("TMC v2 Advertiser Stats: Reporting API: Job ID", extra={'job_id': export_job_id})

        return export_job_id

    def _check_v2_job_status_on_queue(
        self,
        auth_type,
        auth_value,
        export_status_controller,
        export_status_action,
        export_job_id,
        request_retry=None,
    ):
        """Check Job Export Status

        Args:
            export_status_controller:
            export_status_action:
            export_job_id:
            request_retry:

        Returns:

        """
        request_label = "TMC v2 Advertiser Stats: Check Export Status"

        v2_export_status_request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller=export_status_controller,
                action=export_status_action
            )

        request_params = {auth_type: auth_value, "job_id": export_job_id}

        self.logger.info(("TMC v2 Advertiser Stats: Check Job Status"),
                         extra={
                             'action': export_status_action,
                             'job_id': export_job_id,
                             'request_url': v2_export_status_request_url,
                             'request_params': safe_dict(request_params)
                         })

        tries = 60  # -1 (indefinite)
        delay = 10
        jitter = 10
        max_delay = 60

        if request_retry is not None:
            if 'delay' in request_retry:
                delay = request_retry['delay']
            if 'jitter' in request_retry:
                jitter = request_retry['jitter']
            if 'max_delay' in request_retry:
                max_delay = request_retry['max_delay']

            if 'tries' in request_retry:
                tries = request_retry['tries']
            else:
                request_retry.update({'tries': 60})
        else:
            request_retry = {'tries': 60, 'delay': 10, 'timeout': 60}

        self.logger.debug(msg=("TMC v2 Advertiser Stats: Check Job Status: " "Request Retry"), extra=request_retry)

        report_url = None
        _attempts = 1
        export_percent_complete = 0

        time.sleep(10)

        _tries, _delay = tries, delay
        while True:
            try:
                response = self.mv_request.request(
                    request_method="GET",
                    request_url=v2_export_status_request_url,
                    request_params=request_params,
                    request_label=request_label,
                    request_retry_func=self.tune_v2_request_retry_func
                )

            except TuneRequestBaseError as tmc_req_ex:
                self.logger.error(
                    "TMC v2 Advertiser Stats: Check Job Status: Failed",
                    extra=tmc_req_ex.to_dict(),
                )
                raise

            except TuneReportingError as tmc_rep_ex:
                self.logger.error(
                    "TMC v2 Advertiser Stats: Check Job Status: Failed",
                    extra=tmc_rep_ex.to_dict(),
                )
                raise

            except Exception as ex:
                print_traceback(ex)

                self.logger.error("TMC v2 Advertiser Stats: Check Job Status: {}".format(get_exception_message(ex)))
                raise

            http_status_successful = is_http_status_type(
                http_status_code=response.status_code, http_status_type=HttpStatusType.SUCCESSFUL
            )

            if not http_status_successful:
                raise TuneReportingError(
                    error_message=("Failed to get export status on queue: {}").format(response.status_code),
                    error_code=TuneReportingErrorCodes.REP_ERR_REQUEST
                )

            if hasattr(response, 'url'):
                self.logger.info(
                    "TMC v2 Advertiser Stats: Reporting API: Status URL", extra={'response_url': response.url}
                )

            json_response = response.json()

            if not json_response:
                request_status_successful = False

            elif 'status_code' not in json_response:
                request_status_successful = False

            else:
                status_code = json_response['status_code']

                request_status_successful = is_http_status_type(
                    http_status_code=status_code, http_status_type=HttpStatusType.SUCCESSFUL
                )

                errors = None
                if 'errors' in json_response:
                    errors = json_response['errors']

            if not request_status_successful:
                error_message = ("TMC v2 Advertiser Stats: Check Job Status: GET '{}', Failed: {}, {}").format(
                    v2_export_status_request_url, status_code, errors
                )

                if (status_code == TuneReportingError.EX_SRV_ERR_500_INTERNAL_SERVER):
                    self.logger.error(error_message)

                elif (status_code == TuneReportingError.EX_SRV_ERR_503_SERVICE_UNAVAILABLE):
                    self.logger.error(error_message)

                elif (status_code == TuneReportingError.EX_SRV_ERR_504_SERVICE_TIMEOUT):
                    self.logger.error(error_message)
                    continue

                elif (status_code == TuneReportingError.EX_CLT_ERR_408_REQUEST_TIMEOUT):
                    self.logger.error(
                        "GET '{}' request timeout, Retrying: {}".format(v2_export_status_request_url, status_code)
                    )
                    continue

                else:
                    raise TuneReportingError(error_message=error_message, error_code=status_code)

                if tries >= 0 and _tries <= 1:
                    if (status_code == HttpStatusCode.GATEWAY_TIMEOUT):
                        raise TuneReportingError(
                            error_message=error_message, error_code=TuneReportingErrorCodes.GATEWAY_TIMEOUT
                        )
                    elif (status_code == HttpStatusCode.REQUEST_TIMEOUT):
                        raise TuneReportingError(
                            error_message=error_message, error_code=TuneReportingErrorCodes.REQUEST_TIMEOUT
                        )
                    else:
                        raise TuneReportingError(error_message=error_message, error_code=status_code)
                else:
                    self.logger.warning(error_message)

            export_percent_complete = 0
            if 'data' in json_response and json_response['data']:
                json_data = json_response['data']

                if "percent_complete" in json_data:
                    export_percent_complete = \
                        safe_int(json_data["percent_complete"])

                self.logger.info(
                    msg=("TMC v2 Advertiser Stats: "
                         "Check Job Export Status: "
                         "Response Success"),
                    extra={
                        'job_id': export_job_id,
                        'export_status': json_data["status"],
                        'export_percent_complete': safe_int(export_percent_complete),
                        'attempt': _attempts
                    }
                )

                if (export_status_action == TuneV2AdvertiserStatsStatusAction.STATUS):
                    if (export_percent_complete == 100 and json_data["status"] == "complete" and json_data["url"]):
                        report_url = json_data["url"]

                        self.logger.debug(("TMC v2 Advertiser Stats: "
                                           "Check Job Export Status: Completed"),
                                          extra={
                                              'job_id': export_job_id,
                                              'action': export_status_action,
                                              'report_url': report_url,
                                              'request_label': request_label
                                          })

                        break

                elif (export_status_action == TuneV2AdvertiserStatsStatusAction.DOWNLOAD):
                    if (export_percent_complete == 100 and
                            json_data["status"] == "complete" and
                            json_data["data"]["url"]):
                        report_url = json_data["data"]["url"]

                        self.logger.debug(("TMC v2 Advertiser Stats: "
                                           "Check Job Export Status: Completed"),
                                          extra={
                                              'job_id': export_job_id,
                                              'action': export_status_action,
                                              'report_url': report_url,
                                              'request_label': request_label
                                          })

                        break
            else:
                self.logger.debug("TMC v2 Advertiser Stats: " "Check Job Export Status: " "No Data Available")

            if tries >= 0:
                _tries -= 1
                if _tries == 0:
                    self.logger.error(("TMC v2 Advertiser Stats: "
                                       "Check Job Export Status: Exhausted Retries"),
                                      extra={
                                          'attempt': _attempts,
                                          'tries': _tries,
                                          'action': export_status_action,
                                          'request_label': request_label,
                                          'export_percent_complete': safe_int(export_percent_complete),
                                          'job_id': export_job_id
                                      })

                    raise TuneReportingError(
                        error_message=(
                            "TMC v2 Advertiser Stats: "
                            "Check Job Export Status: "
                            "Exhausted Retries: "
                            "Percent Completed: {}"
                        ).format(safe_int(export_percent_complete)),
                        error_code=TuneReportingErrorCodes.REP_ERR_RETRY_EXHAUSTED
                    )

            _attempts += 1

            self.logger.info(
                "TMC v2 Advertiser Stats: Check Job Status",
                extra={'attempt': _attempts,
                       'job_id': export_job_id,
                       'delay': _delay,
                       'action': export_status_action}
            )

            time.sleep(_delay)

            _delay += jitter
            _delay = min(_delay, max_delay)

        if export_percent_complete == 100 and not report_url:
            raise TuneReportingError(
                error_message=("TMC v2 Advertiser Stats: Check Job Export Status: "
                               "Download report URL: Undefined"),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )

        self.logger.info(
            "TMC v2 Advertiser Stats: Check Job Export Status: Finished",
            extra={
                'attempt': _attempts,
                'action': export_status_action,
                'report_url': report_url,
                'request_label': request_label,
                'export_percent_complete': export_percent_complete,
                'job_id': export_job_id
            }
        )

        return report_url

    def _read_stats_data(self, export_job_id, report_url, report_format=None):
        """Read v2 Advertiser Stats Data

        Args:
            export_job_id:
            report_url:
            report_format:

        Returns:

        """
        if not export_job_id:
            raise ValueError("Argument 'job_id' not assigned.")
        if not report_url:
            raise ValueError("Argument 'report_url' not assigned.")

        self.logger.info(
            msg=("TMC v2 Advertiser Stats: "
                 "Start Advertiser Report Stats Read"), extra={'job_id': export_job_id}
        )

        if not report_format:
            path = urlparse(report_url).path
            ext = os.path.splitext(path)[1]
            report_format = ext[1:]

        self.logger.info(
            "TMC v2 Advertiser Stats: Reading", extra={'report_url': report_url,
                                                       'report_format': report_format}
        )

        # pylint: disable=redefined-variable-type
        if report_format == TuneV2AdvertiserStatsFormats.JSON:
            report_reader = ReportReaderJSON(report_url)
        elif report_format == TuneV2AdvertiserStatsFormats.CSV:
            report_reader = ReportReaderCSV(report_url)
        else:
            raise TuneReportingError(
                error_message=("Unexpected Report format: '{}'").format(report_format),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )
        # pylint: enable=redefined-variable-type

        if not report_reader:
            raise TuneReportingError(
                error_message=("Report reader not created for format {}").format(report_format),
                error_code=TuneReportingErrorCodes.REP_ERR_UNEXPECTED_VALUE
            )

        report_reader.read()

        self.logger.info(("TMC v2 Advertiser Stats: " "Finished Advertiser Report Stats read"))

        return report_reader.generator
