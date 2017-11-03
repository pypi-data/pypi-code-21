#
# Copyright (c) 2017 Cisco Systems, Inc. and others.  All rights reserved.
#
__author__ = "mlipman"
__copyright__ = "Copyright(c) 2015, Cisco Systems, Inc."
__version__ = "0.1"
__status__ = "alpha"

import argparse
import io
import sys
import logging
import random
import socket
import ssl
import time
from datetime import datetime, timedelta
from uuid import *
from http import HTTPStatus
import json, base64, string, ast

import requests
import requests.exceptions


from magen_logger.logger_config import LogDefaults, initialize_logger

logger = logging.getLogger(LogDefaults.default_log_name)


# read config file - extract client id, client secret per web app
# "viewer", "ingestion", "webhooks", ...
def read_dict_from_file(filename):
    s = ""
    try:
        with open(filename, "r") as file:
            s = file.read()
    except IOError:
        # caller should log a higher-severity message if appropriate
        logger.debug("Error reading file: %s", filename)
        return {}

    config = ast.literal_eval(s)
    return config

def do_rest_call(method, url, data=None, auth=None, verify=False, headers=None, allow_redirects=True, stream=False):
    """
    This function performs a REST request
    :param method: method for REST request
    :param url: URL used by the REST request
    :param json_req: The JSON used in the request
    :return: True if checks with Response tuple for Flask and response object from requests.request call,
     otherwise False with error string
    """
    try:
        logger.debug("{}ing {}".format(method,url))
        response = requests.request(method=method,
                                    url=url,
                                    data=data,
                                    headers=headers,
                                    auth=auth,
                                    verify=verify,
                                    allow_redirects=allow_redirects,
                                    stream=stream,
                                    timeout=1.0)

        logger.debug("response: text=%s code=%s headers.items=%s", response.text, response.status_code, response.headers.items())
        return True, (response.text, response.status_code, response.headers.items()), response

    except (requests.exceptions.ConnectionError,
            requests.exceptions.RequestException) as exc:
        logger.error(
            'Failed to %s configuration. Server might not be running. Error: %s',
            method, exc)
        return False, "Server might not be running", None
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as exc:
        logger.error(
            'Failed to %s configuration. Server too slow. Error: %s', method, exc)
        return False, "Server too slow", None

#
# string generator that gives more flexibility than templates
#
def html_error(error_string):
    # create a function for this that takes error_link_2 as an argument
    error_link_0 = "<!DOCTYPE html><html lang='en-US'><head><title>Access Denied</title>"
    error_link_1 = "<style type='text/css'>html body {font-family: 'Helvetica', sans-serif; " \
        "font-weight: 300; " \
        "font-size: 15px; color: #333333; background-color: #f7f7f7;} " \
        ".main-container {text-align: center; margin: 100px auto; " \
        "padding: 50px 20px 20px 20px; box-shadow: 0 0 4px 1px #ccc; width: 75%; " \
        "background-color: #fff;} h1 {font-size: 30px; font-weight: 600; margin-bottom: " \
        "30px;} h2 {font-size: 24px; font-weight: 300; margin-bottom: 100px;}" \
        "</style></head><body><div class='main-container'>"
    error_link_2 = error_string + "</div></body></html>"
    error_link = error_link_0 + error_link_1 + error_link_2
    return error_link    
