#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE Advertiser Sites.
"""

import sys
import logging

from requests_mv_integrations.exceptions import (TuneRequestBaseError)
from tune_reporting.errors import (
    print_traceback,
    get_exception_message,
    TuneReportingErrorCodes
)
from tune_reporting.exceptions import (TuneReportingError)
from tune_reporting.support import (python_check_version)
from tune_reporting import (__python_required_version__)
from tune_reporting.tmc.tune_mobileapptracking_api import (TuneMobileAppTrackingApi)
from tune_reporting.tmc.v2.management.tmc_v2_session_authenticate import (TuneV2AuthenticationTypes)
from tune_reporting.tmc.tmc_auth_v2_session_token import (tmc_auth_v2_session_token)
from logging_mv_integrations import (
    LoggingFormat,
    LoggingOutput
)

python_check_version(__python_required_version__)


# @brief TUNE Advertiser Sites.
#
# @namespace tune_reporting.TuneV2AdvertiserSiteStatus
class TuneV2AdvertiserSiteStatus(object):
    """Status states for Advertiser Sites.
    """
    ACTIVE = 1
    NOT_ACTIVE = 2
    ALL = 3


#   TMC v2 Advertiser Sites
#
class TuneV2AdvertiserSites(TuneMobileAppTrackingApi):
    """TMC v2 Advertiser Sites
    """

    # Initialize Job
    #
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR
    ):
        super(TuneV2AdvertiserSites, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output
        )

    # Collect TMC v2 Advertiser Sites
    #
    def collect(
        self,
        auth_value,
        auth_type,
        auth_type_use,
        site_ids=None,
        request_params=None,
        site_status=TuneV2AdvertiserSiteStatus.ACTIVE
    ):
        """Collect TMC v2 Advertiser Sites

        Args:
            tmc_api_key:
            site_ids:
            request_params:
            request_retry:
            site_status:

        Returns:

        """
        if not auth_value:
            raise ValueError("TuneV2AdvertiserSites: Collect: Value 'auth_value' not provided.")
        if not auth_type:
            raise ValueError("TuneV2AdvertiserSites: Collect: Value 'auth_type' not valid.")
        if not auth_type_use or \
                not TuneV2AuthenticationTypes.validate(auth_type_use):
            raise ValueError("TMC v3 Logs Advertisers Base: Collect: Value 'auth_type_use' not valid.")

        _request_params = {"source": "multiverse"}

        if auth_type == TuneV2AuthenticationTypes.API_KEY:
            self.api_key = auth_value

            if auth_type_use == TuneV2AuthenticationTypes.SESSION_TOKEN:
                self.session_token = tmc_auth_v2_session_token(
                    tmc_api_key=self.api_key, logger_level=self.logger_level, logger_format=self.logger_format
                )

                _request_params.update({"session_token": self.session_token,})
            else:
                _request_params.update({"api_key": self.api_key,})

        elif auth_type == TuneV2AuthenticationTypes.SESSION_TOKEN:
            self.session_token = auth_value

            _request_params.update({"session_token": self.session_token,})
        else:
            raise ValueError("Invalid 'auth_type': '{}'".format(auth_type))

        request_url = \
            self.tune_mat_request_path(
                mat_api_version="v2",
                controller="advertiser/sites",
                action="find"
            )

        self.logger.info("Start Advertiser Sites find")

        filter_status = None
        if site_status == TuneV2AdvertiserSiteStatus.ACTIVE:
            filter_status = "(status = \"active\")"
        elif site_status == TuneV2AdvertiserSiteStatus.NOT_ACTIVE:
            filter_status = "(status != \"active\")"

        filter_sites = None
        if site_ids and len(site_ids) > 0:
            filter_sites = "(id IN (" + ",".join(site_ids) + "))"

        if filter_status and filter_sites:
            _request_params["filter"] = "{} AND {}".format(filter_status, filter_sites)
        elif filter_status:
            _request_params["filter"] = filter_status
        elif filter_sites:
            _request_params["filter"] = filter_sites

        if request_params:
            if "filter" in request_params and request_params["filter"]:
                if "filter" in _request_params and _request_params["filter"]:
                    _request_params["filter"] = "({} AND {})".format(
                        _request_params["filter"], request_params["filter"]
                    )
                else:
                    _request_params["filter"] = "({})".format(request_params["filter"])
            _request_params.update({'limit': request_params.get('limit', 0)})
        else:
            _request_params.update({'limit': 0})

        response = None
        try:
            response = self.mv_request.request(
                request_method="GET",
                request_url=request_url,
                request_params=_request_params,
                request_retry=None,
                request_retry_http_status_codes=None,
                request_retry_func=self.tune_v2_request_retry_func,
                request_retry_excps_func=None,
                request_label="{}.{}".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            )

        except TuneRequestBaseError as tmc_req_ex:
            self.logger.error(
                "TuneV2AdvertiserSites: Collect: Failed",
                extra=tmc_req_ex.to_dict(),
            )
            yield (None, tmc_req_ex)

        except TuneReportingError as tmc_rep_ex:
            self.logger.error(
                "TuneV2AdvertiserSites: Collect: Failed",
                extra=tmc_rep_ex.to_dict(),
            )
            yield (None, tmc_rep_ex)

        except Exception as ex:
            print_traceback(ex)

            self.logger.error(get_exception_message(ex))
            yield (None, ex)

        if response:
            json_response = response.json()
            if not json_response or \
                    json_response['status_code'] != 200 or \
                    'errors' in json_response:
                raise TuneReportingError(
                    error_message="Failed to get advertiser sites: {}, {}".format(
                        json_response['status_code'],
                        json_response['errors'].get('message', None),
                    ),
                    error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
                )

            if ('data' not in json_response or not json_response['data']):
                raise TuneReportingError(
                    error_message="Missing 'data': {}".format(str(json_response)),
                    error_code=TuneReportingErrorCodes.REP_ERR_SOFTWARE
                )

            data = json_response['data']
        else:
            data = None

        if not data or len(data) == 0:
            yield ([], None)
        else:
            for (i, item) in enumerate(data):
                yield (item, None)
