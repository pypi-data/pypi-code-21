#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""TUNE MobileAppTracking API base class
"""

import logging

from tune_reporting import (__python_required_version__)
from tune_reporting.support import (python_check_version)
from tune_reporting.tmc.tune_mobileapptracking_api_base import (TuneMobileAppTrackingApiBase)
from tune_reporting.tmc.v2.management.tmc_v2_session_authenticate import (TuneV2SessionAuthenticate)
from logging_mv_integrations import (LoggingFormat, LoggingOutput)

python_check_version(__python_required_version__)


# @brief  TUNE MobileAppTracking API base class
#
# @namespace tune_reporting.TuneMobileAppTrackingApi
class TuneMobileAppTrackingApi(TuneMobileAppTrackingApiBase):
    """TUNE MobileAppTracking API base class
    """

    _TUNE_MANAGEMENT_API_ENDPOINT = "https://api.mobileapptracking.com"

    _FILTER_NOT_DEBUG_NOR_TEST_DATA = (
        "(debug_mode = 0 OR debug_mode is NULL)"
        " AND "
        "(test_profile_id = 0 OR test_profile_id IS NULL)"
    )

    #  Advertiser ID
    #  @var str
    __advertiser_id = None

    # Initialize Job
    #
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=LoggingFormat.JSON,
        logger_output=LoggingOutput.STDOUT_COLOR,
        timezone=None
    ):
        """Initialize

        Args:
            integration:
            logger:
        """
        self.session_token = None
        self.advertiser_id = None

        super(TuneMobileAppTrackingApi, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_output=logger_output,
            timezone=timezone
        )

    def get_session_authenticate(self, tmc_api_key, request_retry=None):
        """Generate session token is returned to provide
        access to service.

        Args:
            tmc_api_key:
            request_retry:

        Returns:

        """
        self.logger.info("TMC API: Session Authenticate: Request")

        tmc_auth_response = self.tmc_auth(tmc_api_key=tmc_api_key)
        assert tmc_auth_response

        tune_v2_session_authenticate = TuneV2SessionAuthenticate(integration_name=self.integration_name)

        if tune_v2_session_authenticate.get_session_token(tmc_api_key=tmc_api_key, request_retry=request_retry):
            self.session_token = tune_v2_session_authenticate.session_token
            return True

        return False
