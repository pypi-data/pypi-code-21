#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertiser Stats Clicks.
"""

import logging
# from pprintpp import pprint

from pytz_convert import (validate_tz_name)
from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from tune_reporting.errors import (print_traceback, get_exception_message)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import (python_check_version)

from .tmc_v3_logs_advertisers_base import (
    TuneV3LogsAdvertisersBase,
    TuneV3LogsAdvertisersActions
)
from tune_reporting import (__python_required_version__)
from tune_reporting.tmc.v2.management.tmc_v2_session_authenticate import (
    TuneV2AuthenticationTypes
)
from logging_mv_integrations import (
    LoggingFormat,
    LoggingOutput
)

python_check_version(__python_required_version__)


# @brief TUNE Advertiser Stats Clicks.
#
# @namespace tune_reporting.TuneV3LogsAdvertisersImpressions
class TuneV3LogsAdvertisersImpressions(TuneV3LogsAdvertisersBase):
    """TUNE V3 Logs Advertiser Impressions.
    """

    _LOGS_ADVERTISERS_TYPE = "impressions"

    # Initialize Job
    #
    def __init__(
        self,
        timezone=None,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR
    ):
        """Initialize TUNE V3 Logs Advertiser Impressions class.
        """
        super(TuneV3LogsAdvertisersImpressions, self).__init__(
            logs_advertisers_type=self._LOGS_ADVERTISERS_TYPE,
            timezone=timezone,
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

    # Collect data: TUNE V3 Logs Advertiser Impressions.
    #
    def _collect(
        self,
        auth_type_use,
        start_date,
        end_date,
        request_params=None,
        request_retry=None,
        request_action=TuneV3LogsAdvertisersActions.FIND,
        auth_type=TuneV2AuthenticationTypes.API_KEY
    ):
        """Collect data: TUNE V3 Logs Advertiser Impressions.

        Args:
            start_date:
            end_date:
            request_params:
            request_retry:
            request_action:

        Returns:

        """
        auth_value = None
        if auth_type_use == TuneV2AuthenticationTypes.API_KEY:
            auth_value = self.api_key
        elif auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
            auth_value = self.session_token

        dict_request_params = {
            auth_type_use: auth_value,
            "timezone": self.timezone,
            "fields": (
                "created,"
                "ad_network_id,"
                "campaign.id,"
                "campaign.name,"
                "publisher.id,"
                "publisher.name,"
                "publisher_ref_id,"
                "publisher_sub_site.id,"
                "publisher_sub_site.ref,"
                "publisher_sub_site.name,"
                "publisher_sub_campaign.id,"
                "publisher_sub_campaign.ref,"
                "publisher_sub_campaign.name,"
                "request_url,"
                "site.id,"
                "site.mobile_app_type,"
                "site.name,"
                "site.package_name,"
                "site.store_app_id"
            ),
            "filter": "({})".format(self._FILTER_NOT_DEBUG_NOR_TEST_DATA),
            "start_date": start_date,
            "end_date": end_date,
            "debug": 0
        }

        if request_params:
            if "fields" in request_params and request_params["fields"]:
                dict_request_params["fields"] = \
                    request_params["fields"]

            if "group" in request_params and request_params["group"]:
                dict_request_params["group"] = \
                    request_params["group"]

            if "timestamp" in request_params and request_params["timestamp"]:
                dict_request_params["timestamp"] = \
                    request_params["timestamp"]

            if "filter" in request_params and request_params["filter"]:
                dict_request_params["filter"] = "({} AND {})".format(
                    request_params["filter"], self._FILTER_NOT_DEBUG_NOR_TEST_DATA
                )

            if "limit" in request_params:
                dict_request_params["limit"] = \
                    int(request_params["limit"])

            if "debug" in request_params:
                dict_request_params["debug"] = \
                    int(request_params["debug"])

            timezone = None
            if "timezone" in request_params:
                timezone = request_params["timezone"]

            if timezone:
                if not validate_tz_name(timezone):
                    return TuneReportingError(error_message="Invalid Timezone: {}".format(timezone))
                self.timezone = timezone
                dict_request_params["timezone"] = \
                    self.timezone

        self.logger.debug(("TMC v3 Logs Advertisers Impressions: "
                           "Action '{}', Params: {}").format(request_action, str(dict_request_params)))

        self.logger.debug(("TMC v3 Logs Advertisers Impressions: " "Timezone: {}").format(self.timezone))

        try:
            if request_action == TuneV3LogsAdvertisersActions.FIND:

                request_params["sorts"] = "created desc"

                self._find_v3(request_params=dict_request_params, request_retry=request_retry)
            elif request_action == TuneV3LogsAdvertisersActions.EXPORT:
                self._export_v3_download_csv(request_params=dict_request_params, request_retry=request_retry)

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Impressions: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            raise

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TMC v3 Logs Advertisers Impressions: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            raise

        except Exception as ex:
            print_traceback(ex)

            self.logger.error("TMC v3 Logs Advertisers Impressions: Failed: {}".format(get_exception_message(ex)))

            raise TuneReportingError(
                error_message=("TMC v3 Logs Advertisers Impressions: Failed: {}").format(get_exception_message(ex)),
                errors=ex
            )
