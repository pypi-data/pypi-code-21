# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utilities to work with docker.

"""


import base64
import json
import os
import traceback
import docker
import re
from azure.cli.core.util import CLIError


def get_docker_client(verb=False):
    try:
        client = docker.from_env()
    except docker.errors.DockerException as exc:
        msg = 'Failed to create Docker client: {}'.format(exc)
        raise CLIError(msg)
    try:
        client.containers.list()
    except docker.errors.APIError as exc:
        api_regex = r'server API version: (?P<server_version>[^\)]+)'
        s = re.search(api_regex, str(exc))
        if s:
            client = docker.DockerClient()
            # specify version 1.24 for now, as that's what runs on centOS DSVM
            client.api = docker.APIClient(base_url='unix://var/run/docker.sock',
                                          version=s.group('server_version'))
        else:
            if verb:
                print(traceback.format_exc())
            raise CLIError("Docker not configured properly. Please check you docker installation.")
    except Exception as ex:
        if verb:
            print(traceback.format_exc())
        raise CLIError("Docker not configured properly. Please check you docker installation.")

    return client
