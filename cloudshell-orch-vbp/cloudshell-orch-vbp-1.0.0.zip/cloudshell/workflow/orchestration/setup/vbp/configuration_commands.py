#!/usr/bin/python
# -*- coding: utf-8 -*-

import cPickle
import traceback

from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

TARGET_TYPE_RESOURCE = "Resource"
PRE_AUTOLOAD_CONFIGURATION_STEPS = "pre_autoload_configuration_command"
PYTHON_DRIVER_CONFIGURE = "configure_device_command"
RESOURCE_COMMAND_CONFIGURE_FAMILIES = ["Virtual Traffic Generator Chassis"]

MISSING_COMMAND_ERROR = "101"
NO_DRIVER_ERR = "129"
DRIVER_FUNCTION_ERROR = "151"


def configure_virtual_chassis(sandbox, components):
    """  """

    message_written = False
    reservation_id = sandbox.id
    logger = sandbox.logger
    api = sandbox.automation_api

    deployed_apps_names = [app.deployed_app.Name for app in components.values()]

    resource_details_cache = {app_name: api.GetResourceDetails(app_name) for app_name in deployed_apps_names}
    resource_cache_pickle_string = cPickle.dumps(resource_details_cache)
    configure_params = [InputNameValue("resource_cache", resource_cache_pickle_string)]

    for app_name in deployed_apps_names:
        app_resource_details = resource_details_cache[app_name]

        if app_resource_details.ResourceFamilyName not in RESOURCE_COMMAND_CONFIGURE_FAMILIES:
            continue

        try:
            logger.info("Called configure resource command on deployed app {0}".format(app_name))
            if not message_written:
                api.WriteMessageToReservationOutput(reservation_id, "Calling configure command on device...")
                message_written = True
            api.ExecuteCommand(reservation_id, app_name, TARGET_TYPE_RESOURCE, PYTHON_DRIVER_CONFIGURE, configure_params)

        except CloudShellAPIError as exc:
            if exc.code not in (NO_DRIVER_ERR,
                                DRIVER_FUNCTION_ERROR,
                                MISSING_COMMAND_ERROR):
                logger.error(
                    "Error executing Configure Resource command on deployed app {0}. Error: {1}".format(
                        app_name,
                        exc.rawxml))
                api.WriteMessageToReservationOutput(reservation_id, "Configuration failed on '{0}': {1}"
                                                    .format(app_name, exc.message))

        except Exception as exc:
            logger.error("Error executing Configure Resource command on deployed app {0}. Error: {1}"
                         .format(app_name, str(exc)))
            api.WriteMessageToReservationOutput(reservation_id, "Configuration failed on '{0}': {1}\n{2}"
                                                .format(app_name, exc.message, traceback.print_exc()))
