# -*- coding: utf-8 -*-

"""
Copyright 2017 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""

# TODO: connect return Connection(client)

import sys
from ._client import Client
from os import path
import logging

logging.basicConfig(level=logging.INFO)


def connect_url(base_url,
                username,
                password,
                ssl_verify=False,
                timeout=None):
    """connect to ATSD using specified parameters

    :param base_url: ATSD url containing protocol, hostname, and port, for example https://atsd_server:8443
    :param username: user name
    :param password: user password
    :param ssl_verify: verify ssl certificate (default False)
    :param timeout: request timeout in seconds (default None - no timeout)
    :return: new client instance
    """

    return Client(base_url, username, password, ssl_verify, timeout)


def connect(file_name=None):
    """connect to ATSD using parameters specified in the configuration file
    (default connection.properties)

    :param file_name: `str`
    """

    if file_name is None:
        file_name = path.join(path.dirname(path.abspath(sys.argv[0])), 'connection.properties')
    f = open(file_name)

    logging.info("Reading connection properties from file: %s" % file_name)

    params = {}
    for line in f:
        k, v = line.split('=')
        params[k.strip()] = v.strip()

    return Client(**params)
