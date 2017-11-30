# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utilities to create and manage realtime web services.

"""

from __future__ import print_function


import docker
import os
import tarfile
import uuid
import requests
import tempfile
from ._docker_utils import get_docker_client
from .._util import cli_context
from .._ml_cli_error import MlCliError
from dateutil import parser

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    # python 2
    from urlparse import urlparse


acs_connection_timeout = 2


def upload_dependency(context, dependency, verbose):
    """

    :param context: CommandLineInterfaceContext object
    :param dependency: path (local, http[s], or wasb[s]) to dependency
    :param verbose: bool indicating verbosity
    :return: (int, str, str): statuscode, uploaded_location, dependency_name
    status codes:
       -1: Error - path does not exist
       0: Success, dependency was already remote or uploaded to blob.
       1: Success, dependency was a directory, uploaded to blob.
    """
    if dependency.startswith('http') or dependency.startswith('wasb'):
        return 0, dependency, urlparse(dependency).path.split('/')[-1]
    if not os.path.exists(dependency):
        if verbose:
            print('Error: no such path {}'.format(dependency))
        return -1, '', ''
    else:
        az_blob_name = str(uuid.uuid4()) + '.tar.gz'
        tmpdir = tempfile.mkdtemp()
        tar_name = os.path.join(tmpdir, az_blob_name)
        dependency_tar = tarfile.open(tar_name, 'w:gz')
        dependency_tar.add(dependency.rstrip(os.sep))
        dependency_tar.close()
        az_container_name = 'amlbdpackages'
        package_location = context.upload_dependency_to_azure_blob(tar_name, az_container_name, az_blob_name)
        print(' {}'.format(dependency))
        return 1, package_location, az_blob_name


def get_container(service_name, all=False, verb=False):
    client = get_docker_client(verb)
    containers = []
    try:
        containers = client.containers.list(all=all, filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to list containers', content=exc)
    if len(containers) == 0:
        print('[Local mode] Error retrieving container details.')
        print('[Local mode] Label should match exactly one container, none found')
        return None
    result_container = None
    for container in containers:
        startedAt = container.attrs.get('State', {}).get('StartedAt', None)
        if startedAt:
            date = parser.parse(startedAt)
            if result_container:
                current_date = parser.parse(result_container.attrs.get('State', {}).get('StartedAt', None))
                if date > current_date:
                    result_container = container
            else:
                result_container = container
    if result_container is None:
        print('[Local mode] Error retrieving container')
        return None
    return result_container


def get_sample_data(swagger_url, headers=None, verbose=False):
    """
    Try to retrieve sample data for the given service.
    :param swagger_url: The url to the service's swagger definition
    :param headers: The headers to pass in the call
    :param verbose: Whether to print debugging info or not.
    :return: str - sample data if available, '' if not available, None if the service does not exist.
    """
    default_retval = None
    if verbose:
        print('[Debug] Fetching sample data from swagger endpoint: {}'.format(swagger_url))
    try:
        swagger_spec_response = requests.get(swagger_url, headers=headers, timeout=acs_connection_timeout)
    except (requests.ConnectionError, requests.exceptions.Timeout):
        if verbose:
            print('[Debug] Could not connect to sample data endpoint on this container.')
        return default_retval

    if swagger_spec_response.status_code == 404:
        if verbose:
            print('[Debug] Received a 404 - no swagger specification for this service.')
        return ''
    elif swagger_spec_response.status_code == 503:
        if verbose:
            print('[Debug] Received a 503 - no such service.')
        return default_retval
    elif swagger_spec_response.status_code != 200:
        if verbose:
            print('[Debug] Received {} - treating as no such service.'.format(swagger_spec_response.status_code))
        return default_retval

    try:
        input_swagger = swagger_spec_response.json()['definitions']['ServiceInput']
        if 'example' in input_swagger:
            sample_data = str(input_swagger['example'])
            sample_data = '"{}"'.format(sample_data.replace("'", '\\"'))
            return sample_data
        else:
            return default_retval
    except ValueError:
        if verbose:
            print('[Debug] Could not deserialize the service\'s swagger specification. Malformed json {}.'.format(
                swagger_spec_response))
        return default_retval


def get_local_webservices(service_name=None, verb=False, context=cli_context):
    """List published realtime web services."""
    if service_name is not None:
        filters = {'label': 'amlid={}'.format(service_name)}
    else:
        filters = {'label': 'amlid'}

    client = get_docker_client(verb)

    try:
        containers = client.containers.list(filters=filters)
        if not containers and service_name:
            raise MlCliError('No service with id {} is running locally.'.format(service_name))
        services = [{
            'Name': container.attrs['Config']['Labels']['amlid'],
            'Id': container.attrs['Config']['Labels']['amlid'],
            'Image': container.attrs['Config']['Image'] if 'Image' in container.attrs else 'Unknown',
            'State': container.attrs['State']['Status'],
            'UpdatedAt': container.attrs['Created']
        } for container in containers]
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to list containers', content=exc)

    return services


def get_local_realtime_service_port(service_name, verbose):
    """Find the host port mapping for a locally published realtime web service."""

    client = get_docker_client(verbose)
    try:
        containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to list docker containers', content=exc)
    if len(containers) == 1:
        container = containers[0]
        port_info_dict = container.attrs['NetworkSettings']['Ports']
        for key in port_info_dict:
            if '5001' in key and len(port_info_dict[key]) == 1:
                port = port_info_dict[key][0]['HostPort']
                if verbose:
                    print('Container port: {}'.format(port))
                return port
        raise MlCliError('Unable to locate expected port info in Ports dictionary: {}'.format(port_info_dict))
    raise MlCliError('Expected exactly one container with label {} and found {}.'.format(
        'amlid={}'.format(service_name), len(containers)))
