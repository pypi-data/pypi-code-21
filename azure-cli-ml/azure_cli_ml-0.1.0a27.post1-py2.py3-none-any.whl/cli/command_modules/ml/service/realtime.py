# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Realtime services functions.

"""

from __future__ import print_function

from ._realtime_local import local_service_create
from ._realtime_local import local_service_run
from ._realtime_local import local_service_delete
from ._realtime_local import local_service_list
from ._realtime_local import local_service_show
from ._realtime_local import local_service_usage
from ._realtime_local import local_service_logs
from ._realtime_mms import mms_service_create
from ._realtime_mms import mms_service_run
from ._realtime_mms import mms_service_update
from ._realtime_mms import mms_service_delete
from ._realtime_mms import mms_service_list
from ._realtime_mms import mms_service_show
from ._realtime_mms import mms_service_keys_handling
from ._realtime_mms import mms_service_usage
from ._realtime_mms import mms_service_logs
from ._realtimeutilities import get_local_realtime_service_port
from ._realtimeutilities import get_sample_data
from .._constants import DEFAULT_INPUT_DATA
from .._constants import SUCCESS_RETURN_CODE
from ..image import _image_create
from .._ml_cli_error import MlCliError
from .._util import cli_context
from .._util import str_to_bool


def realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, target_runtime,
                            app_insights_logging_enabled, model_data_collection_enabled, model_files, num_replicas,
                            image_id, conda_file, autoscale_enabled, autoscale_min_replicas,
                            autoscale_max_replicas, autoscale_target_utilization, autoscale_refresh_period_seconds,
                            cpu, memory, replica_max_concurrent_requests, verb, context=cli_context):
    _realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, target_runtime,
                             app_insights_logging_enabled, model_data_collection_enabled, model_files, num_replicas,
                             image_id, conda_file, autoscale_enabled, autoscale_min_replicas,
                             autoscale_max_replicas, autoscale_target_utilization, autoscale_refresh_period_seconds,
                             cpu, memory, replica_max_concurrent_requests, verb, context)


# TODO Better str_to_bool handling
def _realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, target_runtime,
                             app_insights_logging_enabled, model_data_collection_enabled, model_files, num_replicas,
                             image_id, conda_file, autoscale_enabled, autoscale_min_replicas,
                             autoscale_max_replicas, autoscale_target_utilization, autoscale_refresh_period_seconds,
                             cpu, memory, replica_max_concurrent_requests, verb, context=cli_context):
    if verb:
        print('Starting service create')
    if model_data_collection_enabled:
        model_data_collection_bool = str_to_bool(model_data_collection_enabled)
        if model_data_collection_bool is None:
            raise MlCliError('Error, invalid value provided for model_data_collection_enabled: {}'.format(model_data_collection_enabled))
        model_data_collection_enabled = model_data_collection_bool
    if app_insights_logging_enabled:
        app_insights_bool = str_to_bool(app_insights_logging_enabled)
        if app_insights_bool is None:
            raise MlCliError('Error, invalid value provided for app_insights_logging_enabled: {}'.format(app_insights_logging_enabled))
        app_insights_logging_enabled = app_insights_bool
    if autoscale_enabled:
        autoscale_enabled_bool = str_to_bool(autoscale_enabled)
        if autoscale_enabled_bool is None:
            raise MlCliError('Error, invalid value provided for autoscale_enabled: {}'.format(autoscale_enabled))
        autoscale_enabled = autoscale_enabled_bool

    if context.in_local_mode():
        # Delete any local containers with the same label
        try:
            existing_container_port = get_local_realtime_service_port(service_name, verb)
            print('Found existing local service with the same name running at http://127.0.0.1:{}/score'.format(existing_container_port))
            answer = context.get_input('Delete existing service and create new service (y/N)? ')
            answer = answer.rstrip().lower()
            if answer != 'y' and answer != 'yes':
                print('Canceling service create.')
                return SUCCESS_RETURN_CODE
            local_service_delete(service_name, verb, context)
        except MlCliError:
            pass

    if not image_id:
        image_create_success, image_id = _image_create(service_name[:30], '', None, driver_file,
                                                       schema_file, dependencies, target_runtime, requirements,
                                                       conda_file, model_files, verb, context)
        if image_create_success is not SUCCESS_RETURN_CODE:
            return

    if context.in_local_mode():
        return local_service_create(service_name, image_id, app_insights_logging_enabled, model_data_collection_enabled,
                                    verb, context)
    return mms_service_create(image_id, service_name, app_insights_logging_enabled, model_data_collection_enabled,
                              num_replicas, autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                              autoscale_target_utilization, autoscale_refresh_period_seconds, cpu, memory,
                              replica_max_concurrent_requests, verb, context)


def realtime_service_run(service_id, input_data, verb, context=cli_context):
    _realtime_service_run(service_id, input_data, verb, context)


def _realtime_service_run(service_id, input_data, verb, context=cli_context):
    if verb:
        print("data: {}".format(input_data))

    if context.in_local_mode():
        return local_service_run(service_id, input_data, verb, context)
    return mms_service_run(service_id, input_data, verb, context)


def realtime_service_update(service_id, image_id, num_replicas, model_data_collection_enabled, app_insights_enabled,
                            autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                            autoscale_target_utilization, autoscale_refresh_period_seconds, cpu, memory,
                            replica_max_concurrent_requests, verb, context=cli_context):
    _realtime_service_update(service_id, image_id, num_replicas, model_data_collection_enabled, app_insights_enabled,
                             autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                             autoscale_target_utilization, autoscale_refresh_period_seconds, cpu, memory,
                             replica_max_concurrent_requests, verb, context)


def _realtime_service_update(service_id, image_id, num_replicas, model_data_collection_enabled, app_insights_enabled,
                             autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                             autoscale_target_utilization, autoscale_refresh_period_seconds, cpu, memory,
                             replica_max_concurrent_requests, verb, context=cli_context):
    if context.in_local_mode():
        raise MlCliError('Error, service update not supported for local services.')
    return mms_service_update(service_id, image_id, num_replicas, model_data_collection_enabled, app_insights_enabled,
                              autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                              autoscale_target_utilization, autoscale_refresh_period_seconds, cpu, memory,
                              replica_max_concurrent_requests, verb, context)


def realtime_service_delete(service_id, verb, context=cli_context):
    _realtime_service_delete(service_id, verb, context)


def _realtime_service_delete(service_id, verb, context):
    """Delete a realtime web service."""
    if context.in_local_mode():
        return local_service_delete(service_id, verb, context)
    return mms_service_delete(service_id, verb, context)


def realtime_service_list(verb, context=cli_context):
    _, result = _realtime_service_list(verb, context)
    if context.in_local_mode():
        verb = True
    return result, verb


def _realtime_service_list(verb, context):
    if context.in_local_mode():
        return local_service_list(verb, context)
    return mms_service_list(verb, context)


def realtime_service_show(service_name, service_id, verb, context=cli_context):
    _, result = _realtime_service_show(service_name, service_id, verb, context)
    if context.in_local_mode():
        verb = True
    return result, verb


def _realtime_service_show(service_name, service_id, verb, context):
    """show details of a previously published realtime web service."""
    if not service_id and not service_name:
        raise MlCliError('Error, one of service name or service id must be provided')
    if context.in_local_mode():
        if service_id and not service_name:
            service_name = service_id
        return local_service_show(service_name, verb, context)
    return mms_service_show(service_name, service_id, verb, context)


def realtime_service_keys_handling(service_id, regen, key, verb, context=cli_context):
    _realtime_service_keys_handling(service_id, regen, key, verb, context)


def _realtime_service_keys_handling(service_id, regen, key, verb, context=cli_context):
    if context.in_local_mode():
        raise MlCliError('Key operations not supported for local services')
    return mms_service_keys_handling(service_id, regen, key, verb, context)


def realtime_service_usage(service_id, verb, context=cli_context):
    _realtime_service_usage(service_id, verb, context)


def _realtime_service_usage(service_id, verb, context):
    headers = None
    if context.in_local_mode():
        scoring_url, swagger_url, app_insights_url = local_service_usage(service_id, verb, context)
    else:
        scoring_url, swagger_url, headers, app_insights_url = mms_service_usage(service_id, verb, context)

    input_data = get_sample_data(swagger_url, headers=headers, verbose=verb)
    if not input_data:
        input_data = DEFAULT_INPUT_DATA

    print('Scoring URL:')
    print('    {}'.format(scoring_url))
    print()
    print('Headers:')
    print('    Content-Type: application/json')
    if not context.in_local_mode():
        print('    Authorization: Bearer <key>')
        print('        (<key> can be found by running \'az ml service keys realtime -i {}\')'.format(service_id))
    print()
    print('Swagger URL:')
    print('    {}'.format(swagger_url))
    print()
    print('Sample CLI command:')
    if context.os_is_unix():
        print('    az ml service run realtime -i {} -d {}'.format(service_id, input_data))
    else:
        print('    Usage for cmd: az ml service run realtime -i {} -d {}'.format(service_id, input_data))
        print('    Usage for powershell: az ml service run realtime -i {} --% -d {}'.format(service_id, input_data))
    print()
    print('Sample CURL call:')
    if context.in_local_mode():
        print('    curl -X POST -H "Content-Type:application/json" --data {} {}'.format(input_data, scoring_url))
    else:
        print('    curl -X POST -H "Content-Type:application/json" -H "Authorization:Bearer <key>" --data {} {}'.format(input_data, scoring_url))
    print()
    print('Get debug logs by calling:')
    print('    az ml service logs realtime -i {}'.format(service_id))
    print()
    if app_insights_url:
        print('Get STDOUT/STDERR or Request/Response logs in App Insights:')
        print('    {}'.format(app_insights_url))
    print()
    return SUCCESS_RETURN_CODE


def realtime_service_logs(service_id, request_id, kube_config, max_lines, verb, context=cli_context):
    _realtime_service_logs(service_id, request_id, kube_config, max_lines, verb, context)


def _realtime_service_logs(service_id, request_id, kube_config, max_lines, verb, context):
    if not service_id:
        raise MlCliError('Service ID must be provided.')
    if context.in_local_mode():
        return local_service_logs(service_id, request_id, verb)
    return mms_service_logs(service_id, request_id, kube_config, max_lines, verb, context)
