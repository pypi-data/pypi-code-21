#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting.errors

from requests_mv_integrations.errors import error_name as tune_requests_error_name
from requests_mv_integrations.errors import error_desc as tune_requests_error_desc

tune_reporting_error_name = {
    700: 'Reporting Error',
    707: 'Request Error',
    708: 'Software Error',
    710: 'Unexpected Value',
    721: 'Job Stopped',
    722: 'Retry Exhausted',
    760: 'Auth Error',
    761: 'Auth JSON Error',
    766: 'JSON Decoding Error',
    799: 'Unexpected Error'
}

tune_reporting_error_description = {
    -1: 'Unassiged exit condition',
    0: 'Successfully completed',
    700: 'Reporting error occurred',
    707: 'Unexpected request failure',
    708: 'Unexpected software error was detected',
    710: 'Unexpected value returned',
    721: 'Job Stopped',
    722: 'Retry Exhausted',
    760: 'Auth Error',
    761: 'Auth JSON Error',
    766: 'JSON Decoding Error',
    799: 'Unexpected Error'
}


def error_name(error_code):
    """Provide definition of Error Code

    Args:
        error_code:

    Returns:

    """
    if error_code is None or not isinstance(error_code, int):
        return "Error Code: Invalid Type: {}".format(error_code)

    error_code_name_ = tune_requests_error_name(error_code, return_bool=True)
    if error_code_name_ and error_code_name_ is not None:
        return error_code_name_

    error_code_name_ = tune_reporting_error_name.get(error_code, None)
    if error_code_name_ is not None:
        return error_code_name_

    return "Error Code: Undefined: {}".format(error_code)


def error_desc(error_code):
    """Provide definition of Error Code

    Args:
        error_code:

    Returns:

    """
    if error_code is None or not isinstance(error_code, int):
        return "Error Code: Invalid Type: {}".format(error_code)

    error_code_description_ = tune_requests_error_desc(error_code, return_bool=True)
    if error_code_description_ and error_code_description_ is not None:
        return error_code_description_

    error_code_description_ = tune_reporting_error_description.get(error_code, None)
    if error_code_description_ is not None:
        return error_code_description_

    return "Error Code: Undefined: {}".format(error_code)
