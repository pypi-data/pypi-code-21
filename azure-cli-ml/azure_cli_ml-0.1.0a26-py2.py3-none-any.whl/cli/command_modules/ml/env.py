from builtins import input
from ._util import cli_context
from ._util import CLIError
from ._az_util import validate_env_name
from ._az_util import InvalidNameError
from ..ml import __version__
import azure.cli.core.azlogging as azlogging
from ._constants import MLC_CLIENT_ENUMS_PATH
from .compute import compute_create
from .compute import _start_kubectl_proxy
from importlib import import_module
mlc_client_enums = import_module(MLC_CLIENT_ENUMS_PATH, package=__package__)
OperationStatus = mlc_client_enums.OperationStatus
logger = azlogging.get_az_logger(__name__)


def version():
    print('Azure Machine Learning Command Line Tools {}'.format(__version__))


def env_local(context=cli_context):
    """
    Switch the current execution context to 'local'
    :param context: 
    :return: 
    """
    _switch_current_execution_mode('local', context)


def env_cluster(context=cli_context):
    """
    Switch the current execution context to 'cluster'
    :param context: 
    :return: 
    """
    if context.current_env and context.current_env['cluster_type'].lower() == 'local':
        raise CLIError('Error, currently set environment does not support cluster mode.\n'
                       'Please either run \'az ml env set\' to set a different environment,\n'
                       'or run \'az ml env setup\' to provision a new environment.')
    _switch_current_execution_mode('cluster', context)


def _switch_current_execution_mode(mode, context, disable_dashboard=False):
    if context.current_execution_mode:
        if context.current_execution_mode != mode:
            new_compute = context.current_env
            new_compute['current_execution_mode'] = mode
            context.set_compute(new_compute)
            if mode == 'cluster' and not disable_dashboard:
                _start_kubectl_proxy(context.current_compute_resource_group, context.current_compute_name, context)
        print('Now running in {} mode'.format(mode))
    else:
        raise CLIError('Error, unable to switch to {} mode, current environment not set.\n'
                       'Please run \'az ml env set\' to set a current environment\n'
                       'or \'az ml env setup\' to setup a new environment'.format(mode))


def env_setup(name, cluster, service_principal_app_id,
              service_principal_password, agent_count, agent_vm_size, location=None, resource_group=None,
              yes=False, cert_pem=None, key_pem=None, storage_arm_id=None, acr_arm_id=None,
              cert_cname=None, master_count=1, context=cli_context, verb=False):
    """
    Sets up an MLC environment.
    :param name:
    :param cluster:
    :param service_principal_app_id:
    :param service_principal_password:
    :param location:
    :param resource_group:
    :param agent_count:
    :param yes: bool Run without interaction. Will fail if not logged in.
    :param context:
    :return:
    """

    root_name = name
    try:
        validate_env_name(root_name)
    except InvalidNameError as e:
        raise CLIError('Invalid environment name. {}'.format(e.message))

    if cluster:
        compute_type = 'cluster'
        try:
            if context.in_local_mode():
                print('Found currently set local environment')
                storage_arm_id, acr_arm_id = prompt_for_resource_reuse(storage_arm_id, acr_arm_id, context)
        except CLIError:
            pass
    else:
        compute_type = 'local'
    return compute_create(root_name, service_principal_app_id,
                          service_principal_password, location, agent_count, agent_vm_size, resource_group,
                          yes, cert_pem, key_pem, storage_arm_id, acr_arm_id, cert_cname,
                          master_count, compute_type, context, verb)


def prompt_for_resource_reuse(storage_arm_id, acr_arm_id, context):
    answer = context.get_input('Reuse storage and ACR (Y/n)?').lower()
    if answer != 'n' and answer != 'no':
        storage_arm_id = context.current_env['storage_account']['resourceId']
        acr_arm_id = context.current_env['container_registry']['resourceId']
        print('Continuing setup with current storage and acr')
    return storage_arm_id, acr_arm_id
