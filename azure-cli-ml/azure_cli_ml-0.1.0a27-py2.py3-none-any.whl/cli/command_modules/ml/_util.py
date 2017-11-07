# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utility functions for AML CLI
"""

from __future__ import print_function
import os
import json
import sys
import platform
import socket
import time
import yaml
import tempfile
from datetime import datetime, timedelta
from pkg_resources import working_set
from ._ml_cli_error import MlCliError

try:
    # python 3
    from urllib.request import pathname2url
    from urllib.parse import urljoin, urlparse  # pylint: disable=unused-import
    import socketserver as SocketServer
except ImportError:
    # python 2
    from urllib import pathname2url
    from urlparse import urljoin, urlparse
    import SocketServer

import subprocess
import re
import shutil
import requests
from tabulate import tabulate
from builtins import input
from azure.storage.blob import (BlobPermissions, BlockBlobService, ContentSettings)
from azure.cli.core._profile import Profile
from azure.cli.core.util import CLIError
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import MMS_ASYNC_OPERATION_POLLING_MAX_TRIES
from ._constants import MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS
from ._constants import MMS_PAGINATED_RESPONSE_MAX_TRIES
from ._acs_util import merge_kubernetes_yamls
from azureml.api.realtime.services import generate_main
import azure.cli.core.azlogging as azlogging
logger = azlogging.get_az_logger(__name__)

ice_base_url = 'https://amlacsagent.azureml-int.net'
acs_connection_timeout = 5
ice_connection_timeout = 15


# EXCEPTIONS
class InvalidConfError(Exception):
    """Exception raised when config read from file is not valid json."""
    pass


# CONTEXT CLASS
class CommandLineInterfaceContext(object):
    """
    Context object that handles interaction with shell, filesystem, and azure blobs
    """
    hdi_home_regex = r'(.*:\/\/)?(?P<cluster_name>[^\s]*)'
    aml_env_default_location = 'east us'
    model_dc_storage = os.environ.get('AML_MODEL_DC_STORAGE')
    model_dc_event_hub = os.environ.get('AML_MODEL_DC_EVENT_HUB')
    hdi_home = os.environ.get('AML_HDI_CLUSTER')
    base_name = os.environ.get('AML_ROOT_NAME')
    hdi_user = os.environ.get('AML_HDI_USER', '')
    hdi_pw = os.environ.get('AML_HDI_PW', '')
    env_is_k8s = os.environ.get('AML_ACS_IS_K8S', '').lower() == 'true'
    k8s_batch_url = os.environ.get('AML_K8S_BATCH_URL')


    @property
    def app_insights_account_key(self):
        if not self._app_insights_account_key:
            self._app_insights_account_key = self.get_from_mlc(('app_insights', 'instrumentation_key'))
        return self._app_insights_account_key

    @property
    def app_insights_account_id(self):
        if not self._app_insights_account_id:
            self._app_insights_account_id = self.get_from_mlc(('app_insights', 'app_id'))
        return self._app_insights_account_id

    @property
    def az_account_name(self):
        if not self._account_name:
            self._account_name = self.get_from_mlc(('storage_account', 'resource_id'))
            if self._account_name and self._account_name.startswith('/subscriptions'):
                self._account_name = self._account_name.split('/')[-1]
        return self._account_name

    @property
    def az_account_key(self):
        if not self._account_key:
            self._account_key = self.get_from_mlc(('storage_account', 'primary_key'))
        return self._account_key

    @property
    def acr_home(self):
        if not self._acr_home:
            self._acr_home = self.get_from_mlc(('container_registry', 'login_server'))
        return self._acr_home

    @property
    def acr_pw(self):
        if not self._acr_pw:
            self._acr_pw = self.get_from_mlc(('container_registry', 'password'))
        return self._acr_pw

    @property
    def acr_user(self):
        if not self._acr_user:
            if not self.acr_home:
                self._acr_user = None
            else:
                self._acr_user = self.acr_home.split('.')[0]
        return self._acr_user

    def __init__(self):
        self.env_profile_path = os.path.join(get_home_dir(), '.azure', 'viennaOperationalizationComputeResource.json')
        self.az_container_name = 'azureml'
        if self.hdi_home:
            outer_match_obj = re.match(self.hdi_home_regex, self.hdi_home)
            if outer_match_obj:
                self.hdi_home = outer_match_obj.group('cluster_name')
        self.hdi_domain = self.hdi_home.split('.')[0] if self.hdi_home else None
        self.forwarded_port = None
        self.current_execution_mode = None
        self.current_compute_creds = None
        self.current_compute_name = None
        self.current_compute_resource_group = None
        self.current_compute_subscription_id = None
        self.current_env = self.read_config()
        if self.current_env:
            self.current_execution_mode = self.current_env['current_execution_mode']
            self.current_compute_resource_group = self.current_env['resource_group']
            self.current_compute_name = self.current_env['name']
            self.current_compute_subscription_id = self.current_env['subscription']
        self._account_name = None
        self._account_key = None
        self._acr_home = None
        self._acr_pw = None
        self._acr_user = None
        self._app_insights_account_key = None
        self._app_insights_account_id = None

    @staticmethod
    def get_active_subscription_id():
        return Profile().get_subscription()['id']

    @staticmethod
    def set_active_subscription_id(sub_id):
        Profile().set_active_subscription(sub_id)
        print('Active subscription set to {}'.format(sub_id))

    def set_compute(self, compute_resource):
        self.write_config(compute_resource)
        self.current_env = compute_resource
        self.current_compute_resource_group = compute_resource['resource_group']
        self.current_compute_name = compute_resource['name']
        self.current_compute_subscription_id = compute_resource['subscription']
        self.current_execution_mode = compute_resource['current_execution_mode']

    def validate_active_and_compute_subscriptions(self):
        if (self.current_compute_subscription_id is not None and
                    self.current_compute_subscription_id != self.get_active_subscription_id()):
            print('Your current active subscription ({}) is not the same as the '
                  'subscription for your environment ({}). To proceed, you must '
                  'update your active environment.'.format(self.get_active_subscription_id(),
                                                           self.current_compute_subscription_id))
            result = input('Would you like to update your active subscription to {} [Y/n]? '.format(self.current_compute_subscription_id)).lower()
            if result == 'n' or result == 'no':
                raise MlCliError('Unable to get current compute resource from different subscription.')

            self.set_active_subscription_id(self.current_compute_subscription_id)

    def populate_compute_creds(self):
        from ._compute_util import get_compute_resource_keys
        if self.current_compute_creds is None:
            if self.current_compute_name and self.current_compute_resource_group:
                self.validate_active_and_compute_subscriptions()
                try:
                    # cache credentials
                    self.current_compute_creds = get_compute_resource_keys(self.current_compute_resource_group,
                                                                           self.current_compute_name)
                except CLIError:
                    self.unset_current_compute_and_warn_user()
                    raise

    def unset_current_compute_and_warn_user(self):
        logger.warning('Unable to find env with group {} and name {}. It may have been moved or deleted, '
                       'or you could have the wrong active subscription set. Unsetting current env.'.format(
            self.current_compute_resource_group,
            self.current_compute_name))
        logger.warning("To see available environments in the subscription, run:\n"
                       "  az ml env list\n"
                       "To set an active environment, run:\n"
                       "  az ml env set -n <env_name> -g <env_group>\n"
                       "To see available subscriptions, run:\n"
                       "  az account show -o table\n"
                       "To set active accout, run:\n"
                       "  az account set -s <subscription_name>\n")

        os.remove(self.env_profile_path)
        self.current_compute_resource_group = None
        self.current_compute_name = None

    def raise_for_missing_creds(self):
        raise MlCliError('Running in cluster mode is only supported with MLC RP environments. '
                         'You can provision a new environment by running: '
                         '\'az ml env setup -c -n <cluster name> -g <resource group>\'. '
                         'If you have already provisioned an environment, set it as your active environment by running:'
                         '\'az ml env set -n <cluster name> -g <resource group>\'')

    def update_kube_config(self):
        from ._k8s_util import K8sConstants
        self.populate_compute_creds()
        if not self.current_compute_creds:
            self.raise_for_missing_creds()
        # read kubeconfig from creds
        try:
            new = yaml.safe_load(self.current_compute_creds.container_service.acs_kube_config)
        except yaml.parser.ParserError as ex:
            raise MlCliError('Error parsing {}'.format(self.current_compute_creds.container_service.acs_kube_config), content=ex)

        # read kubeconfig on file
        if os.path.exists(K8sConstants.KUBE_CONFIG_PATH):
            try:
                with open(K8sConstants.KUBE_CONFIG_PATH) as stream:
                    existing = yaml.safe_load(stream)
            except (IOError, OSError) as ex:
                raise MlCliError('Error loading kube config.', content=ex)
            except yaml.parser.ParserError as ex:
                raise MlCliError('Error parsing yaml', content=ex)

            if existing is None:
                raise MlCliError('Failed to load existing configuration from {}'.format(existing))

            # merge
            merged = merge_kubernetes_yamls(existing, new)
        else:
            kube_dir = os.path.dirname(K8sConstants.KUBE_CONFIG_PATH)
            if not os.path.exists(kube_dir):
                os.makedirs(kube_dir)
            merged = new

        with open(K8sConstants.KUBE_CONFIG_PATH, 'w') as kube_config:
            yaml.safe_dump(merged, kube_config, default_flow_style=True)

    def get_from_mlc(self, cred_path):
        self.populate_compute_creds()
        if self.current_compute_creds is None:
            raise MlCliError('Unable to determine current environment information. '
                             'Please run \'az ml env set\'')

        try:
            trav = self.current_compute_creds
            for step in cred_path:
                trav = getattr(trav, step)
        except AttributeError as exc:
            raise MlCliError('Encountered an issue parsing credentials for compute. '
                             'Please contact deployml@microsoft.com with this information '
                             'if this issue persists. Raw credentials: {}'.format(self.current_compute_creds),
                             content=exc)
        return trav

    @staticmethod
    def str_from_subprocess_communicate(output):
        """

        :param output: bytes or str object
        :return: str version of output
        """
        if isinstance(output, bytes):
            return output.decode('utf-8')
        return output

    def run_cmd(self, cmd_list):
        """

        :param cmd: str command to run
        :return: str, str - std_out, std_err
        """
        proc = subprocess.Popen(cmd_list, shell=(not self.os_is_unix()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return self.str_from_subprocess_communicate(output), \
               self.str_from_subprocess_communicate(err)

    def read_config(self):
        """

        Tries to read in ~/.azure/viennaOperationalizationComputeResource.json as a dictionary.
        :return: dict - if successful, the config dictionary from ~/.azure/viennaOperationalizationComputeResource.json, None otherwise
        :raises: InvalidConfError if the configuration read is not valid json, or is not a dictionary
        """
        try:
            with open(self.env_profile_path, 'r') as env_file:
                try:
                    current_env = json.load(env_file)
                except ValueError as e:
                    os.remove(self.env_profile_path)
                    raise MlCliError('Error retrieving currently set environment: invalid JSON. '
                                     'Please run \'az ml env set\'')
        except IOError:
            return None
        return current_env

    def write_config(self, compute_resource):
        """

        Writes out the given configuration dictionary to ~/.azure/viennaOperationalizationComputeResource.json
        :param compute_resource: Configuration dictionary.
        :return: 0 if success, -1 otherwise
        """
        try:
            with open(self.env_profile_path, 'w') as conf_file:
                conf_file.write(json.dumps(compute_resource))
        except IOError:
            return -1

        return 0

    def in_local_mode(self):
        """
        Determines if AML CLI is running in local mode
        :return: bool - True if in local mode, false otherwise
        """

        if self.current_execution_mode:
            return self.current_execution_mode == 'local'
        else:
            raise MlCliError('Error retrieving currently set environment. '
                             'Please run \'az ml env set\'')


    def upload_resource(self, filepath, container, asset_id):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :return: str location of uploaded resource
        """
        az_blob_name = '{}/{}'.format(container, asset_id)
        bbs = BlockBlobService(account_name=self.az_account_name,
                               account_key=self.az_account_key)
        bbs.create_container(self.az_container_name)
        bbs.create_blob_from_path(self.az_container_name, az_blob_name, filepath)
        return 'wasbs://{}@{}.blob.core.windows.net/' \
               '{}'.format(self.az_container_name, self.az_account_name, az_blob_name)

    def upload_dependency_to_azure_blob(self, filepath, container, asset_id,
                                        content_type='application/octet-stream'):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :param content_type: str content mime type
        :return: str sas url to uploaded dependency
        """
        bbs = BlockBlobService(account_name=self.az_account_name,
                               account_key=self.az_account_key)
        bbs.create_container(container)
        bbs.create_blob_from_path(container, asset_id, filepath,
                                  content_settings=ContentSettings(
                                      content_type=content_type))
        blob_sas = bbs.generate_blob_shared_access_signature(
            container_name=container,
            blob_name=asset_id,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(days=30)
        )
        return 'http://{}.blob.core.windows.net/' \
               '{}/{}?{}'.format(self.az_account_name, container, asset_id, blob_sas)

    @staticmethod
    def cache_local_resource(filepath, container, asset_id):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :return: str location of cached resource
        """

        # create a cached version of the asset
        dest_dir = os.path.join(get_home_dir(), '.azuremlcli', container)
        if os.path.exists(dest_dir):
            if not os.path.isdir(dest_dir):
                raise ValueError('Expected asset container {} to be a directory if it'
                                 'exists'.format(dest_dir))
        else:
            try:
                os.makedirs(dest_dir)
            except OSError as exc:
                raise ValueError('Error creating asset directory {} '
                                 'for asset {}: {}'.format(dest_dir, asset_id, exc))
        dest_filepath = os.path.join(dest_dir, asset_id)
        if os.path.isfile(filepath):
            shutil.copyfile(filepath, dest_filepath)
        elif os.path.isdir(filepath):
            shutil.copytree(filepath, dest_filepath)
        else:
            raise ValueError('Assets must be a file or directory.')
        return dest_filepath

    @staticmethod
    def http_call(http_method, url, **kwargs):
        """

        :param http_method: str: (post|get|put|delete)
        :param url: str url to perform http call on
        :return: requests.response object
        """
        http_method = http_method.lower()

        # raises AttributeError if not a valid method
        return getattr(requests, http_method)(url, **kwargs)

    @staticmethod
    def get_args():
        return sys.argv

    @staticmethod
    def os_is_unix():
        return platform.system().lower() in ['linux', 'unix', 'darwin']

    @staticmethod
    def get_input(input_str):
        return input(input_str)

    @staticmethod
    def get_socket(inet, stream):
        return socket.socket(inet, stream)

    def check_call(self, cmd):
        return subprocess.check_call(cmd, shell=(not self.os_is_unix()))

    def check_output(self, cmd, stderr=None):
        return subprocess.check_output(cmd, shell=(not self.os_is_unix()), stderr=stderr)

    def get_batch_auth(self):
        """
        Get correct authorization headers
        :param context:
        :return:
        """
        if self.env_is_k8s:
            # Currently we have no Authorization around Kubernetes services
            return None
        return self.hdi_user, self.hdi_pw


class JupyterContext(CommandLineInterfaceContext):
    def __init__(self):
        super(JupyterContext, self).__init__()
        self.local_mode = True
        self.input_response = {}

    def in_local_mode(self):
        return self.local_mode

    def set_input_response(self, prompt, response):
        self.input_response[prompt] = response

    def get_input(self, prompt):
        return self.input_response[prompt]


# UTILITY FUNCTIONS
def get_json(payload, pascal=False):
    """
    Handles decoding JSON to python objects in py2, py3
    :param payload: str/bytes json to decode
    :return: dict/list/str that represents json
    """
    if isinstance(payload, bytes):
        payload = payload.decode('utf-8')
    payload = json.loads(payload) if payload else {}
    if pascal:
        payload = to_pascal(payload)
    return payload


def get_home_dir():
    """
    Function to find home directory on windows or linux environment
    :return: str - path to home directory
    """
    return os.path.expanduser('~')


cli_context = CommandLineInterfaceContext()


def check_version(context, conf):
    """
    :param context: CommandLineInterfaceContext object
    :param conf: dict configuration dictionary
    :return: None
    """
    try:
        output, _ = context.run_cmd('pip search azuremlcli')
        installed_regex = r'INSTALLED:[\s]+(?P<current>[^\s]*)'
        latest_regex = r'LATEST:[\s]+(?P<latest>[^\s]*)'
        latest_search = re.search(latest_regex, output)
        if latest_search:
            installed_search = re.search(installed_regex, output)
            if installed_search:
                print('\033[93mYou are using AzureML CLI version {}, '
                      'but version {} is available.'.format(
                    installed_search.group('current'), latest_search.group('latest')))
                print("You should consider upgrading via the 'pip install --upgrade "
                      "azuremlcli' command.\033[0m")
                print()
        conf['next_version_check'] = (datetime.now() + timedelta(days=1)).strftime(
            '%Y-%m-%d')
        context.write_config(conf)
    except Exception as exc:
        print('Warning: Error determining if there is a newer version of AzureML CLI '
              'available: {}'.format(exc))


def get_success_and_resp_str(context, http_response, response_obj=None, verbose=False):
    """

    :param context:
    :param http_response: requests.response object
    :param response_obj: Response object to format a successful response
    :param verbose: bool - flag to increase verbosity
    :return: (bool, str) - (result, result_str)
    """
    if http_response is None:
        return False, "Response was None."
    if verbose:
        print(http_response.content)
    try:
        http_response.raise_for_status()
        json_obj = get_json(http_response.content, pascal=True)
        if response_obj is not None:
            return True, response_obj.format_successful_response(context, json_obj)
        return True, json.dumps(json_obj, indent=4, sort_keys=True)

    except ValueError:
        return True, http_response.content

    except requests.exceptions.HTTPError:
        return False, process_errors(http_response)


def print_util(msg, verb):
    if verb:
        print(msg)


def process_errors(http_response):
    """

    :param http_response:
    :return: str message for parsed error
    """
    try:
        json_obj = get_json(http_response.content)
        to_print = '\n'.join(
            [detail['message'] for detail in json_obj['error']['details']])
    except (ValueError, KeyError):
        to_print = http_response.content

    return 'Failed.\nResponse code: {}\n{}'.format(http_response.status_code, to_print)


def upload_directory(context, filepath, container, verbose):
    """

    :param context: CommandLineInterfaceContext object
    :param filepath: str path to directory to upload
    :param container: str name of container to upload to
    :param verbose: bool flag to increase verbosity
    :return: (str, str) (asset_id, location)
    """
    wasb_path = None
    to_strip = os.path.split(filepath)[0]

    for dirpath, _, files in os.walk(filepath):
        for walk_fp in files:
            to_upload = os.path.join(dirpath, walk_fp)
            container_for_upload = '{}/{}'.format(container, to_upload[
                                                             len(to_strip) + 1:-(
                                                             len(walk_fp) + 1)].replace(
                '\\', '/'))
            _, wasb_path = upload_resource(context, to_upload, container_for_upload,
                                           walk_fp,
                                           verbose)

    if wasb_path is None:
        raise ValueError('Directory {} was empty.'.format(filepath))

    asset_id = os.path.basename(filepath)
    match_obj = re.match(r'(?P<wasb_path>.*{})'.format(os.path.basename(filepath)),
                         wasb_path)
    if match_obj:
        return asset_id, match_obj.group('wasb_path')
    raise ValueError('Unable to parse upload location.')


def upload_resource(context, filepath, container, asset_id, verbose):
    """
    Function to upload local resource to blob storage
    :param context: CommandLineInterfaceContext object
    :param filepath: str path of file to upload
    :param container: str name of subcontainer inside azureml container
    :param asset_id: str name of asset inside subcontainer
    :param verbose: bool verbosity flag
    :return: str, str : uploaded asset id, blob location
    """
    wasb_package_location = context.upload_resource(filepath, container, asset_id)
    if verbose:
        print("Asset {} uploaded to {}".format(filepath, wasb_package_location))
    return asset_id, wasb_package_location


def traverse_json(json_obj, traversal_tuple):
    """
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here, but can work in the case that
        a valid numerical index is passed in the tuple

    :param json_obj: json_obj to traverse. nested dictionaries--lists not supported
    :param traversal_tuple: tuple of keys to traverse the json dict
    :return: string value to display
    """
    trav = to_pascal(json_obj)
    for key in traversal_tuple:
        trav = trav[key]
    return trav


class Response(object):  # pylint: disable=too-few-public-methods
    """
    Interface for use constructing response strings from json object for successful requests
    """

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        raise NotImplementedError('Class does not implement format_successful_response')


class StaticStringResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Class for use constructing responses that are a static string for successful requests.
    """

    def __init__(self, static_string):
        self.static_string = static_string

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        return self.static_string


class TableResponse(Response):
    """
    Class for use constructing response tables from json object for successful requests
    """

    def __init__(self, header_to_value_fn_dict):
        """

        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        self.header_to_value_fn_dict = header_to_value_fn_dict

    def create_row(self, context, json_obj, headers):
        """

        :param json_obj: list or dict to present as table
        :param headers: list of str: headers of table
        :return:
        """
        return [self.header_to_value_fn_dict[header].set_json(json_obj).evaluate(context)
                for header in headers]

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: list or dict to present as table
        :return: str response to print to user
        """
        rows = []
        headers = self.header_to_value_fn_dict.keys()
        if isinstance(json_obj, list):
            for inner_obj in json_obj:
                rows.append(self.create_row(context, inner_obj, headers))
        else:
            rows.append(self.create_row(context, json_obj, headers))
        return tabulate(rows, headers=[header.upper() for header in headers],
                        tablefmt='psql')


class PaginatedTableResponse(TableResponse):
    def __init__(self, value_wrapper, header_to_value_fn_dict):
        self.value_wrapper = value_wrapper
        super(PaginatedTableResponse, self).__init__(header_to_value_fn_dict)

    def format_successful_response(self, context, json_obj):
        if isinstance(json_obj, dict) and self.value_wrapper in json_obj:
            values = json_obj[self.value_wrapper]
        else:
            values = json_obj
        return super(PaginatedTableResponse, self).format_successful_response(context, values)


class MultiTableResponse(TableResponse):
    """
    Class for use building responses with multiple tables
    """

    def __init__(self,
                 header_to_value_fn_dicts):  # pylint: disable=super-init-not-called
        """

        :param header_to_value_fn_dicts:
        """

        self.header_to_value_fn_dicts = header_to_value_fn_dicts

    def format_successful_response(self, context, json_obj):
        result = ''
        for header_to_value_fn_dict in self.header_to_value_fn_dicts:
            self.header_to_value_fn_dict = header_to_value_fn_dict
            result += super(MultiTableResponse, self).format_successful_response(context,
                                                                                 json_obj)
            result += '\n'
        return result


class StaticStringWithTableReponse(TableResponse):
    """
    Class for use constructing response that is a static string and tables from json object for successful requests
    """

    def __init__(self, static_string, header_to_value_fn_dict):
        """
        :param static_string: str that will be printed after table
        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        super(StaticStringWithTableReponse, self).__init__(header_to_value_fn_dict)
        self.static_string = static_string

    def format_successful_response(self, context, json_obj):
        return '\n\n'.join([super(StaticStringWithTableReponse,
                                  self).format_successful_response(context, json_obj),
                            self.static_string])


class ValueFunction(object):
    """
    Abstract class for use finding the appropriate value for a given property in a json response.
         defines set_json, a function for storing the json response we will format
         declares evaluate, a function for retrieving the formatted string
    """

    def __init__(self):
        self.json_obj = None

    def set_json(self, json_obj):
        """

        :param json_obj: list or dict to store for processing
        :return: ValueFunction the "self" object with newly updated json_obj member
        """
        self.json_obj = json_obj
        return self

    def evaluate(self, context):
        """

        :param context:
        :return: str value to display
        """
        raise NotImplementedError("Class does not implement evaluate method.")


class TraversalFunction(ValueFunction):
    """
    ValueFunction that consumes a traversal tuple to locate the appropriate string for display
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here.
    """

    def __init__(self, tup):
        super(TraversalFunction, self).__init__()
        self.traversal_tup = tup

    def evaluate(self, context):
        return traverse_json(self.json_obj, self.traversal_tup)


class ConditionalListTraversalFunction(TraversalFunction):
    """
    Class for use executing actions on members of a list that meet certain criteria
    """

    def __init__(self, tup, condition, action):
        super(ConditionalListTraversalFunction, self).__init__(tup)
        self.condition = condition
        self.action = action

    def evaluate(self, context):
        json_list = super(ConditionalListTraversalFunction, self).evaluate(context)
        return ', '.join(
            [self.action(item) for item in json_list if self.condition(item)])


def is_int(int_str):
    """

    Check whether the given variable can be cast to int
    :param int_str: the variable to check
    :return: bool
    """
    try:
        int(int_str)
        return True
    except ValueError:
        return False


def to_pascal(obj):
    """ Make dictionary PascalCase """
    if isinstance(obj, dict):
        return {k[0].upper() + k[1:]: to_pascal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_pascal(k) for k in obj]
    return obj


def add_sdk_to_requirements(requirements):
    # always pass sdk as dependency to mms/ICE.
    # Add the version required by the installed CLI.
    generated_requirements = tempfile.mkstemp(suffix='.txt', prefix='requirements')[1]
    req_str = ''
    if requirements:
        with open(requirements) as user_requirements:
            req_str = user_requirements.read()

    with open(generated_requirements, 'w') as generated_requirements_file:
        generated_requirements_file.write('{}\n{}\n'.format(
            req_str.strip(),
            [dist for dist in working_set.by_key[
                'azure-cli-ml'].requires() if dist.key == 'azureml-model-management-sdk'][0]))

    return generated_requirements


def get_auth_header():
    from ._az_util import az_login
    az_login()
    profile = Profile()
    cred, sub, tenant = profile.get_login_credentials()
    return cred.signed_session().headers['Authorization']


def wrap_driver_file(driver_file, schema_file, dependencies):
    """

    :param driver_file: str path to driver file
    :param schema_file: str path to schema file
    :param dependencies: list of str paths to dependencies
    :return: str path to wrapped driver file
    """
    new_driver_loc = tempfile.mkstemp(suffix='.py')[1]
    print('Creating new driver at {}'.format(new_driver_loc))
    dependencies.append(driver_file)
    if not os.path.exists(driver_file):
        raise MlCliError('Path to driver file {} does not exist.'.format(driver_file))
    if not schema_file:
        schema_file = ''
    else:
        # Fix path references in schema file,
        # since the container it will run in is a Linux container
        path_components = schema_file.split(os.sep)
        schema_file = "/".join(path_components)
    return generate_main(driver_file, schema_file, new_driver_loc)


def query_mms_async_operation(operation_url, operation_headers, params, context):
    polling_iteration = 0
    while polling_iteration < MMS_ASYNC_OPERATION_POLLING_MAX_TRIES:
        try:
            operation_resp = context.http_call('get', operation_url, params=params, headers=operation_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
            break
        except requests.ConnectionError:
            raise MlCliError('Error connecting to {}.'.format(operation_url))
        except requests.Timeout:
            print('Operation request timed out, trying again')
            polling_iteration += 1
            time.sleep(MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS)

    if polling_iteration == MMS_ASYNC_OPERATION_POLLING_MAX_TRIES:
        raise MlCliError('Error, operation request to {} timed out.'.format(operation_url))

    if operation_resp.status_code == 200:
        return get_json(operation_resp.content, pascal=True), operation_resp.headers
    else:
        raise MlCliError('Error occurred while polling for operation at {}.'.format(operation_url), operation_resp.headers, operation_resp.content, operation_resp.status_code)


def poll_mms_async_operation(operation_url, operation_headers, params, polling_max_tries, context):
    resp_obj, headers_obj = query_mms_async_operation(operation_url, operation_headers, params, context)

    polling_iteration = 0
    while 'State' in resp_obj and polling_iteration < polling_max_tries:
        operation_state = resp_obj['State']

        if operation_state == 'NotStarted' or operation_state == 'Running':
            time.sleep(MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS)
            sys.stdout.write('.')
            sys.stdout.flush()
            polling_iteration += 1
        elif operation_state == 'Succeeded':
            try:
                resource_id = resp_obj['ResourceLocation'].split('/')[-1]
            except KeyError:
                raise MlCliError('Invalid response key: ResourceLocation')
            return resource_id
        else:
            sys.stdout.write('Failed\n')
            sys.stdout.flush()
            return resp_obj, headers_obj

        resp_obj, headers_obj = query_mms_async_operation(operation_url, operation_headers, params, context)

    if polling_iteration == polling_max_tries:
        raise MlCliError('Error, operation polling timed out')
    else:
        raise MlCliError('Error, "State" not found in operation response: {}'.format(resp_obj))


def get_paginated_results(resp, headers, context):
    result = get_json(resp.content, pascal=True)
    try:
        items = result['Value']
    except ValueError:
        raise MlCliError('Error, unable to get key \'Value\' from paginated response: {}'.format(result))
    while 'NextLink' in result.keys():
        next_link = result['NextLink']
        polling_iteration = 0
        while polling_iteration < MMS_PAGINATED_RESPONSE_MAX_TRIES:
            try:
                resp = context.http_call('get', next_link, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
                break
            except requests.ConnectionError:
                raise MlCliError('Error connecting to {}.'.format(next_link))
            except requests.Timeout:
                print('Request timed out, trying again')
                polling_iteration += 1
                time.sleep(MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS)

        if polling_iteration == MMS_PAGINATED_RESPONSE_MAX_TRIES:
            raise MlCliError('Error, request to {} timed out.'.format(next_link))

        result = get_json(resp.content, pascal=True)
        try:
            items = items + result['Value']
        except ValueError:
            raise MlCliError('Error, unable to get key \'Value\' from paginated response: {}'.format(result))

    return items


def str_to_bool(str):
    str = str.lower()
    if str == 'true':
        return True
    elif str == 'false':
        return False
    else:
        return None


def conditional_update_or_remove(dictionary, tup, value):
    trav = dictionary
    for key in tup[:-1]:
        trav = trav[key]
    if value:
        trav[tup[-1]] = value
    else:
        del trav[tup[-1]]
