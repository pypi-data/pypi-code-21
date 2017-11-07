#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertiser Stats Actuals.
"""

import logging
#from pprintpp import pprint
from pytz_convert import (validate_tz_name)
from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from safe_cast import safe_dict
from tune_reporting.errors import (
    print_traceback,
    get_exception_message,
    TuneReportingErrorCodes
)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import (python_check_version)
from .tmc_v2_advertiser_stats_base import (
    TuneV2AdvertiserStatsBase,
    TuneV2AdvertiserStatsActions,
    TuneV2AuthenticationTypes,
)
from tune_reporting import (__python_required_version__)
from logging_mv_integrations import (LoggingFormat, LoggingOutput)
log = logging.getLogger(__name__)

python_check_version(__python_required_version__)


# @brief TUNE Advertiser Stats Actuals.
#
# @namespace tune_reporting.TuneV2AdvertiserStatsActuals
class TuneV2AdvertiserStatsActuals(TuneV2AdvertiserStatsBase):
    """TMC v2 Advertiser Stats.
    """

    _CONTROLLER = "advertiser/stats"

    # Initialize Job
    #
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR,
        timezone=None
    ):
        """Initialize TMC v2 Advertiser Stats Class.
        """
        super(TuneV2AdvertiserStatsActuals, self).__init__(
            controller=self._CONTROLLER,
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output,
            timezone=timezone
        )

    # Collect data: TMC v2 Advertiser Stats Actuals.
    #
    def _collect(
        self,
        auth_type_use,
        start_date,
        end_date,
        tmp_directory=None,
        request_params=None,
        request_retry=None,
        request_action=TuneV2AdvertiserStatsActions.FIND
    ):
        """Collect data: TUNE Advertiser Stats Actuals.

        Args:
            start_date:
            end_date:
            request_params:
            request_retry:
            request_action:

        Returns:

        """
        self.logger.debug(("TuneV2AdvertiserStatsActuals: Collect: " "Action: '{}'").format(request_action))
        dict_request_params = self._map_request_params(auth_type_use, start_date, end_date, request_params)

        self.logger.debug("TuneV2AdvertiserStatsActuals: Collect", extra={'build_params': dict_request_params})

        try:
            if request_action == TuneV2AdvertiserStatsActions.FIND:
                self._find_v2(request_params=dict_request_params, request_retry=request_retry)
            elif request_action == TuneV2AdvertiserStatsActions.EXPORT:
                assert tmp_directory
                self._export_v2_download_csv(
                    tmp_directory=tmp_directory,
                    auth_type_use=auth_type_use,
                    export_controller=self._CONTROLLER,
                    export_action='export',
                    export_status_controller=self._CONTROLLER,
                    export_status_action='status',
                    request_params=dict_request_params,
                    request_retry=request_retry
                )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TuneV2AdvertiserStatsActuals: Collect: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TuneV2AdvertiserStatsActuals: Collect: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TuneV2AdvertiserStatsActuals: Collect: {}".format(get_exception_message(ex)))

            raise TuneReportingError(
                error_message=("TuneV2AdvertiserStatsActuals: Collect: Failed: {}").format(get_exception_message(ex)),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

    # Collect data: TUNE Advertiser Stats Actuals.
    #
    def _stream_v2(
        self,
        auth_type_use,
        start_date,
        end_date,
        request_params,
        request_retry=None,
    ):
        """Stream data: TUNE Advertiser Stats Actuals.

        Args:
            start_date:
            end_date:
            request_params:
            request_retry:

        Returns:

        """
        self.logger.debug("TuneV2AdvertiserStatsActuals: Stream: Export", extra={'request_params': request_params})

        dict_request_params = self._map_request_params(auth_type_use, start_date, end_date, request_params)

        self.logger.debug("TuneV2AdvertiserStatsActuals: Stream: Export", extra={'build_params': dict_request_params})

        try:
            response = self._export_stream_v2(
                auth_type_use,
                export_controller=self._CONTROLLER,
                export_action='export',
                export_status_controller=self._CONTROLLER,
                export_status_action='status',
                request_params=dict_request_params,
                request_retry=request_retry
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TuneV2AdvertiserStatsActuals: Stream: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TuneV2AdvertiserStatsActuals: Stream: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TuneV2AdvertiserStatsActuals: {}".format(get_exception_message(ex)))

            raise TuneReportingError(
                error_message=("TuneV2AdvertiserStatsActuals: Failed: {}").format(get_exception_message(ex)),
                errors=ex,
                error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
            )

        return response

    def _map_request_params(self, auth_type_use, start_date, end_date, request_params=None):
        """Build Request Paramaters

        Args:
            start_date:
            end_date:
            request_params:

        Returns:

        """
        auth_value = None
        if auth_type_use == TuneV2AuthenticationTypes.API_KEY:
            auth_value = self.api_key
        elif auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
            auth_value = self.session_token

        dict_request_params = {
            auth_type_use: auth_value,
            "source": "multiverse",
            "response_timezone": self.timezone,
            "timestamp": "datehour",
            "group": (
                "advertiser_id,"
                "country_id,"
                "currency_code,"
                "is_reengagement,"
                "platform,"
                "publisher_id,"
                "publisher_sub_ad_id,"
                "publisher_sub_adgroup_id,"
                "publisher_sub_campaign_id,"
                "publisher_sub_publisher_id,"
                "publisher_sub_site_id,"
                "purchase_validation_status,"
                "site_id"
            ),
            "fields": (
                "ad_clicks,"
                "ad_clicks_unique,"
                "ad_impressions,"
                "ad_impressions_unique,"
                "ad_network_id,"
                "advertiser_id,"
                "conversions,"
                "country.code,"
                "country.name,"
                "currency_code,"
                "date_hour,"
                "events,"
                "installs,"
                "is_reengagement,"
                "payouts,"
                "publisher.name,"
                "publisher_id,"
                "publisher_sub_ad.ref,"
                "publisher_sub_adgroup.ref,"
                "publisher_sub_campaign.ref,"
                "publisher_sub_publisher.ref,"
                "publisher_sub_site.ref,"
                "site.mobile_app_type,"
                "site.package_name,"
                "site.store_app_id,"
                "site_id"
            ),
            "filter": "({})".format(self._FILTER_NOT_DEBUG_NOR_TEST_DATA),
            "start_date": start_date,
            "end_date": end_date,
            "debug": 0
        }

        if request_params:
            self.logger.debug(
                "TuneV2AdvertiserStatsActuals: Request", extra={'request_params': safe_dict(request_params)}
            )

            if "fields" in request_params and \
                    request_params["fields"]:
                dict_request_params["fields"] = \
                    request_params["fields"]

            if "group" in request_params and \
                    request_params["group"]:
                dict_request_params["group"] = \
                    request_params["group"]

            if "timestamp" in request_params and \
                    request_params["timestamp"]:
                dict_request_params["timestamp"] = \
                    request_params["timestamp"]

            if "filter" in request_params and \
                    request_params["filter"]:
                dict_request_params["filter"] = "({} AND {})".format(
                    request_params["filter"], self._FILTER_NOT_DEBUG_NOR_TEST_DATA
                )

            if "format" in request_params:
                dict_request_params["format"] = \
                    request_params["format"]

            if "offset" in request_params:
                dict_request_params["offset"] = \
                    int(request_params["offset"])

            if "page" in request_params:
                dict_request_params["page"] = \
                    int(request_params["page"])

            if "limit" in request_params:
                dict_request_params["limit"] = \
                    int(request_params["limit"])

            if "debug" in request_params:
                dict_request_params["debug"] = \
                    int(request_params["debug"])

            response_timezone = None
            if "timezone" in request_params:
                response_timezone = request_params["timezone"]
            if "response_timezone" in request_params:
                response_timezone = request_params["response_timezone"]

            if response_timezone:
                if not validate_tz_name(response_timezone):
                    return TuneReportingError(error_message="Invalid Timezone: {}".format(response_timezone))
                self.timezone = response_timezone
                dict_request_params["response_timezone"] = \
                    self.timezone

        self.logger.debug(("TuneV2AdvertiserStatsActuals: " "Timezone: {}").format(self.timezone))

        return dict_request_params
