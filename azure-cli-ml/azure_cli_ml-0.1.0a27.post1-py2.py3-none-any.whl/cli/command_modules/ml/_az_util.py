# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utilities to interact with the Azure CLI (az).

"""

import datetime
import requests
import re
import os
import yaml
import errno
import platform
import stat
from azure.cli.core._profile import Profile
from azure.cli.core._config import az_config
from azure.cli.core.commands import client_factory
from azure.cli.core.commands import LongRunningOperation
import azure.cli.core.azlogging as azlogging
from azure.mgmt.containerregistry.container_registry_management_client import \
    ContainerRegistryManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentProperties
from ._constants import DATA_DIRECTORY
from ._util import cli_context
from ._ml_cli_error import MlCliError

from azure.cli.core.util import get_file_json
from azure.cli.core.util import CLIError

logger = azlogging.get_az_logger(__name__)

# add constructor for unicode to safe loader, as we were previously
# using dump instead of safe_dump
yaml.SafeLoader.add_constructor("tag:yaml.org,2002:python/unicode",
                                lambda loader, node: node.value)


def validate_env_name(name):
    """
    Validate the given name against Azure storage naming rules
    :param name: The name to validate
    :return: None, if valid. Throws an exception otherwise.
    """
    if not name or len(name) > 20:
        raise MlCliError('Invalid environment name. Name must be between 1 and 20 characters in length.')

    if not bool(re.match('^[a-z0-9]+$', name)):
        raise MlCliError('Invalid environment name. Name must only contain lowercase alphanumeric characters.')


def az_login(app_id=None, client_secret=None, tenant=None, yes=False):
    """Log in to Azure if not already logged in
    :return None
    """
    profile = Profile()
    if app_id and client_secret and tenant:
        profile.find_subscriptions_on_login(False, app_id, client_secret, True, tenant)
        return

    # interactive login
    try:
        profile.get_subscription()
    except CLIError as exc:
        # thrown when not logged in
        if "'az login'" in str(exc):
            if yes:
                raise MlCliError('Unable to run with -y flag until you are logged in. Attempt to get subscription '
                                 'failed: {}'.format(exc))
            profile.find_subscriptions_on_login(True, None, None, None, None)
        elif "'az account set'" in str(exc):
            # TODO - figure out what to do here..
            raise
        else:
            raise


def az_check_subscription(yes=False, context=cli_context):
    """
    Check whether the user wants to use the current default subscription
    Assumes user is logged in to az.
    """
    profile = Profile()
    current_subscription = profile.get_subscription()['name']
    if yes:
        return current_subscription
    print('Subscription set to {}'.format(current_subscription))
    answer = context.get_input('Continue with this subscription (Y/n)? ')
    answer = answer.rstrip().lower()
    if answer == 'n' or answer == 'no':
        print("Available subscriptions:\n  {}".format('\n  '.join(
            [sub['name'] for sub in profile.load_cached_subscriptions()])))
        new_subscription = context.get_input('Enter subscription name: ').rstrip()
        az_set_active_subscription(new_subscription)
    return profile.get_subscription()['name']


def az_get_active_subscription_id():
    return Profile().get_subscription()['id']


def az_set_active_subscription(subscription):
    profile = Profile()
    profile.set_active_subscription(
        profile.get_subscription(subscription)['name'])
    print('Active subscription updated to {}'.format(
        profile.get_subscription()['name']))


def az_create_resource_group(context, root_name, append='rg', location=None):
    """Create a resource group using root_name as a prefix"""

    rg_name = root_name + append
    rg_client = client_factory.get_mgmt_service_client(
        ResourceManagementClient).resource_groups

    if rg_client.check_existence(rg_name):
        print('Resource group {} already exists, skipping creation.'.format(rg_name))
    else:
        print("Creating resource group {}".format(rg_name))
        rg_client.create_or_update(
            rg_name,
            ResourceGroup(location=location or context.aml_env_default_location)
        )

    return rg_name


def az_register_provider(namespace):
    """ Registers a given resource provider with Azure."""
    client = client_factory.get_mgmt_service_client(ResourceManagementClient).providers
    client.register(namespace)


def az_get_provider(namespace):
    """ Registers a given resource provider with Azure."""
    client = client_factory.get_mgmt_service_client(ResourceManagementClient).providers
    return client.get(namespace)


def get_acr_api_version():
    return az_config.get('acr', 'apiversion', None)


def az_create_storage_and_acr(root_name, resource_group):
    """
    Create an ACR registry using the Azure CLI (az).
    :param root_name: The prefix to attach to the ACR name.
    :param resource_group: The resource group in which to create the ACR.
    :return: Tuple - the ACR login server, username, and password, storage_name, storage_key
    """
    arm_client = client_factory.get_mgmt_service_client(ResourceManagementClient)
    location = arm_client.resource_groups.get(resource_group).location
    acr_name = root_name + 'acr'
    storage_account_name = root_name + 'stor'

    print(
    'Creating ACR registry and storage account: {} and {} (please be patient, this can take several minutes)'.format(
        acr_name, storage_account_name))
    parameters = {
        'registryName': {'value': acr_name},
        'registryLocation': {'value': location},
        'registrySku': {'value': 'Basic'},
        'adminUserEnabled': {'value': True},
        'storageAccountName': {'value': storage_account_name}
    }
    custom_api_version = get_acr_api_version()
    if custom_api_version:
        parameters['registryApiVersion'] = {'value': custom_api_version}

    template = get_file_json(os.path.join(DATA_DIRECTORY, 'acrtemplate.json'))
    properties = DeploymentProperties(template=template, parameters=parameters,
                                      mode='incremental')
    deployment_client = client_factory.get_mgmt_service_client(
        ResourceManagementClient).deployments
    deployment_name = resource_group + 'deploymentacr' + datetime.datetime.now().strftime(
        '%Y%m%d%I%M%S')

    # deploy via template
    LongRunningOperation()(
        deployment_client.create_or_update(resource_group, deployment_name, properties))

    # fetch finished storage and keys
    storage_client = client_factory.get_mgmt_service_client(
        StorageManagementClient).storage_accounts
    keys = storage_client.list_keys(resource_group, storage_account_name).keys

    # fetch finished registry and credentials
    if custom_api_version:
        acr_client = client_factory.get_mgmt_service_client(
            ContainerRegistryManagementClient,
            api_version=custom_api_version).registries
    else:
        acr_client = client_factory.get_mgmt_service_client(
            ContainerRegistryManagementClient).registries
    registry = acr_client.get(resource_group, acr_name)
    acr_creds = acr_client.list_credentials(resource_group, acr_name)
    return registry.login_server, acr_creds.username, acr_creds.passwords[
        0].value, storage_account_name, keys[0].value


def az_get_app_insights_account(completed_deployment):
    """
    Gets the app insights account which has finished deploying. It assumes that the user
    is already logged in to Azure, and that the Azure CLI (az) is present on the system.
    :param completed_deployment: The dictionary object returned from the completed template deployment.
    :return: A tuple of the app insights account name and instrumentation key.
    """
    rp_namespace = 'microsoft.insights'
    resource_type = 'components'
    resource_name = completed_deployment.properties.parameters['appName']['value']
    resource_group = completed_deployment.name.split('deployment')[0]
    rcf = client_factory.get_mgmt_service_client(ResourceManagementClient)
    provider = rcf.providers.get(rp_namespace)
    resource_types = [t for t in provider.resource_types
                      if t.resource_type.lower() == resource_type]
    if len(resource_types) != 1 or not resource_types[0].api_versions:
        raise MlCliError('Error finding api version for App Insights.')
    non_preview_versions = [v for v in resource_types[0].api_versions
                            if 'preview' not in v.lower()]
    api_version = non_preview_versions[0] if non_preview_versions else \
        resource_types[0].api_versions[0]
    resource_client = rcf.resources
    result = resource_client.get(resource_group, rp_namespace, '', resource_type,
                                 resource_name, api_version)
    return resource_name, result.properties['InstrumentationKey']


def register_acs_providers():
    from azure.mgmt.resource.resources import ResourceManagementClient
    rm_client = client_factory.get_mgmt_service_client(ResourceManagementClient)
    providers = rm_client.providers
    namespaces = ['Microsoft.Network', 'Microsoft.Compute', 'Microsoft.Storage']
    for namespace in namespaces:
        state = providers.get(resource_provider_namespace=namespace)
        if state.registration_state != 'Registered':  # pylint: disable=no-member
            logger.info('registering %s', namespace)
            providers.register(resource_provider_namespace=namespace)
        else:
            logger.info('%s is already registered', namespace)


def _makedirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def k8s_install_cli(client_version='latest', install_location=None):
    """
    Downloads the kubectl command line from Kubernetes
    """

    if client_version == 'latest':
        resp = requests.get(
            'https://storage.googleapis.com/kubernetes-release/release/stable.txt')
        resp.raise_for_status()
        client_version = resp.content.decode().strip()

    system = platform.system()
    base_url = 'https://storage.googleapis.com/kubernetes-release/release/{}/bin/{}/amd64/{}'
    if system == 'Windows':
        file_url = base_url.format(client_version, 'windows', 'kubectl.exe')
    elif system == 'Linux':
        # TODO: Support ARM CPU here
        file_url = base_url.format(client_version, 'linux', 'kubectl')
    elif system == 'Darwin':
        file_url = base_url.format(client_version, 'darwin', 'kubectl')
    else:

        raise MlCliError('Proxy server ({}) does not exist on the cluster.'.format(system))

    logger.warning('Downloading client to %s from %s', install_location, file_url)
    try:
        with open(install_location, 'wb') as kubectl:
            resp = requests.get(file_url)
            resp.raise_for_status()
            kubectl.write(resp.content)
            os.chmod(install_location,
                     os.stat(
                         install_location).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        logger.warning('Ensure {} is on the path to avoid seeing this message in the future.'.format(install_location))
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
        raise MlCliError('Connection error while attempting to download client', content=err)


def kubectl_path(context):
    executable = 'kubectl' if context.os_is_unix() else 'kubectl.exe'
    return os.path.join(os.path.expanduser('~'), 'bin', executable)


def az_install_kubectl(context):
    """Downloads kubectl from kubernetes.io and adds it to the system path."""
    full_install_path = kubectl_path(context)
    _makedirs(os.path.dirname(full_install_path))
    os.environ['PATH'] += os.pathsep + os.path.dirname(full_install_path)
    k8s_install_cli(install_location=full_install_path)
    return True


def az_delete_rg(rg_name):
    rg_client = client_factory.get_mgmt_service_client(
        ResourceManagementClient).resource_groups
    rg_client.delete(rg_name)
