"""Common library client API for dataClay.

Note that importing this module has a basic semantic: it prepares the dataClay
core and sets the "client" mode for the library.
"""
from communication.grpc.clients.lm_client import LMClient
from dataclay import runtime, RuntimeType
import dataclay
from dataclay.conf import settings
from dataclay.core import constants
import dataclay.core
from dataclay.core.paraver import trace_function
from dataclay.management import track_local_available_classes
import logging
import os
import sys

from ._prepare import *
from ._prepare import UNDEFINED_LOCAL as _UNDEFINED_LOCAL

# This will be populated during initialization
LOCAL = _UNDEFINED_LOCAL

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

__all__ = ["init", "finish"]

logger = logging.getLogger('dataclay.api')
_connection_initialized = False
_initialized = False


def is_initialized():
    """Simple query for the _initialized flag.

    :return: True if `init` has already been called, False otherwise.
    """
    return _initialized


def reinitialize_clients():
    logger.info("Performing reinitialization of clients, removing #%s cached ones and recreating LMClient",
                len(runtime.ready_clients))
    runtime.ready_clients = {
        "@LM": LMClient(settings.logicmodule_host, settings.logicmodule_port),
    }


@trace_function
def init_connection(client_file):
    """Initialize the connection client ==> LogicModule.

    Note that the connection can be initialized standalone from here (like the
    dataClay tool performs) or it can be initialized by the full init() call.

    :param client_file: The path to the `client.properties` file. If set to None,
    then this function assumes that the connection settings are already loaded.
    :return: The LogicModule client (also accessible through the global
    runtime.ready_clients["@LM"]
    """
    global _connection_initialized
    if _connection_initialized:
        return runtime.ready_clients["@LM"]

    if client_file:
        settings.load_connection(client_file)

    # Once the properties are load, we can prepare the LM client
    client = LMClient(settings.logicmodule_host, settings.logicmodule_port)
    runtime.ready_clients["@LM"] = client

    _connection_initialized = True
    return client


@trace_function
def get_backends():
    """Return all the dataClay backend present in the system."""
    return runtime.get_execution_environments_info()


@trace_function
def init(config_file="./cfgfiles/session.properties"):
    """Initialization made on the client-side, with file-based settings.

    Note that after a successful call to this method, subsequent calls will be
    a no-operation.

    :param config_file: The configuration file that will be used. If explicitly
    set to null, then its value will be retrieved from the DATACLAYSESSIONCONFIG
    environment variable.
    """
    global _connection_initialized
    global _initialized
    if _initialized:
        return

    if not config_file:
        config_file = os.environ["DATACLAYSESSIONCONFIG"]

    settings.load_properties(config_file)

    client = init_connection(None)

    # In all cases, track (done through babelstubs YAML file)
    contracts = track_local_available_classes()

    # Ensure they are in the path (high "priority")
    sys.path.insert(0, os.path.join(settings.stubs_folder, 'sources'))

    # Use the stored contract list (one per line)

    session_info = client.new_session(
        settings.current_id,
        settings.current_credential,
        contracts,
        settings.datasets,
        settings.dataset_for_store,
        constants.lang_codes.LANG_PYTHON
    )
    settings.current_session_id = session_info.sessionID

    name = settings.local_backend_name
    if name:
        exec_envs = runtime.get_execution_environments_info()
        for k, v in exec_envs.iteritems():
            if exec_envs[k].name == name:
                global LOCAL
                LOCAL = k
                break
        else:
            logger.warning("Backend with name '%s' not found, ignoring", name)

    settings.dataset_id = client.get_dataset_id(
        settings.current_id,
        settings.current_credential,
        settings.dataset_for_store)

    # The new_session RPC may fall, and thus we will consider
    # the library as "not initialized". Arriving here means "all ok".
    _initialized = True


@trace_function
def finish():
    logger.info("Finishing dataClay API")

    for name, client in runtime.ready_clients.iteritems():
        logger.verbose("Closing client connection to %s", name)
        client.close()

    if settings.paraver_tracing_enabled:
        logger.debug("Closing paraver output")
        dataclay.core.prv.close()


######################################
# Static initialization of dataClay
##########################################################

# We are the client, so populate accordingly
runtime.establish(RuntimeType.client, {
    'get_object_by_id': get_object_by_id,
    'get_execution_environment_by_oid': get_execution_environment_by_oid,
    'get_execution_environments_info': get_execution_environments_info,
    'make_persistent': make_persistent,
    'execute_implementation_aux': execute_implementation_aux,
    'store_object': store_object,
    'new_instance': new_instance,
    'get_by_alias': get_by_alias,
    'delete_alias': delete_alias,
    'move_object': move_object,
}, {
    # Store all the classes locally deployed, to know the mapping between MetaClassID<->full_name
    'local_available_classes': dict(),
})

# The client should never need the delete methods of persistent objects
# ... not doing this is a performance hit
del dataclay.DataClayObject.__del__

dataclay.core.initialize()
# Now the logger is ready
logger.info("Client-mode initialized, dataclay.runtime should be ready")
