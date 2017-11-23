"""The basic dataClay server features for Python Execution Environments.

This module provides the Execution Environment for Python. A basic dataClay
infrastructure is required, mainly:

  - Logic Module
  - Storage Locations
  - [optional] More Execution Environments

Note that this server must be aware of the "local" Storage Location and the
central Logic Module node.
"""
import atexit
from communication.grpc.clients.ee_client import EEClient
from communication.grpc.clients.lm_client import LMClient
from communication.grpc.generated.dataservice import dataservice_pb2_grpc as ds
from communication.grpc.server.ee_server import DataServiceEE
from concurrent import futures
from dataclay import runtime, RuntimeType
from dataclay.conf import settings
from dataclay.core.constants import lang_codes
from dataclay.core.network.exceptions import RemoteException
from dataclay.core.paraver import trace_function
from dataclay.managers import metaclass_containers
from dataclay.managers.objects import cached_objects_dict
import gc
import grpc
import logging
import os
import socket
import sys
import time

from . import operations
from ._prepare import *
from .config import set_defaults


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

logger = logging.getLogger(__name__)


def reset_caches():
    logger.info("Received SIGHUP --proceeding to reset caches")
    metaclass_containers.cached_metaclass_info.clear()
    metaclass_containers.cached_metaclasses.clear()
    cached_objects_dict.clear()


@atexit.register
def persist_and_exit():
    logger.info("Performing exit hook --persisting files")

    # Stop the GC --now we will take care of everything manually
    gc.disable()

    # CAUTION! This is normally an invalid `for`, because inmemory_objects
    # is a WeakValueDictionary for which data may change while iterating.
    # However, we have just disabled the GC, so we should be covered.
    for o in runtime.inmemory_objects.values():
        dco_extradata = o._dclay_instance_extradata
        if not dco_extradata.persistent_flag or \
                not dco_extradata.loaded_flag:
            # Nothing to do for this particular object
            pass

        logger.debug("Proceeding to persist object %s", dco_extradata.object_id)
        runtime.store_object(o)

    # Avoid futher calls (the GC will call again,
    # but most likely it will be under an invalid state of modules)
    runtime.teardown()

    # Let the GC strike again
    gc.enable()


@trace_function
def preface_autoregister():
    """Perform a pre-initialization of stuff (prior to the autoregister call)."""

    # logger.info("Preface Autoregister")

    # Check if there is an explicit IP for autoregistering
    local_ip = os.getenv("DATASERVICE_HOST", "")
    if not local_ip:
        local_ip = socket.gethostbyname(socket.gethostname())

    logger.info("Starting client to LogicModule at %s:%d",
                 settings.logicmodule_host, settings.logicmodule_port)

    lm_client = LMClient(settings.logicmodule_host, settings.logicmodule_port)

    # Leave the ready client to the LogicModule globally available
    runtime.ready_clients["@LM"] = lm_client

    # logger.info("local_ip %s returned", local_ip)
    return local_ip


@trace_function
def start_autoregister(local_ip):
    """Start the autoregister procedure to introduce ourselves to the LogicModule."""
    logger.info("Start Autoregister with %s local_ip", local_ip)
    lm_client = runtime.ready_clients["@LM"]

    success = False
    retries = 0
    while not success:
        try:
            storage_location_id, execution_environment_id = lm_client.lm_autoregister_ds(
                settings.dataservice_name,
                local_ip,
                settings.dataservice_port,
                lang_codes.LANG_PYTHON)
        except (RemoteException, socket.error) as e:
            logger.debug("Catched exception of type %s. Message:\n%s", type(e), e)
            if retries > 12:
                logger.warn("Could not create channel, aborting (reraising exception)")
                raise
            else:
                logger.info("Could not create channel, retry #%d of 12 in 5 seconds" % retries)
                # FIXME: Not Very performing, find a better way
                time.sleep(5)
                retries += 1
        else:
            success = True

    logger.info("Current DataService autoregistered. Associated StorageLocationID: %s",
                storage_location_id)
    settings.storage_id = storage_location_id
    settings.environment_id = execution_environment_id

    # Retrieve the storage_location connection data
    storage_location = lm_client.get_storage_location_for_ds(storage_location_id)

    logger.debug("StorageLocation data: {name: '%s', hostname: '%s', port: %d}",
                 storage_location.name,
                 storage_location.hostname,
                 storage_location.storageTCPPort)

    logger.info("Starting client to StorageLocation {%s} at %s:%d",
                storage_location_id, storage_location.hostname, storage_location.storageTCPPort)

    storage_client = EEClient(storage_location.hostname, storage_location.storageTCPPort)

    # Leave the ready client to the Storage Location globally available
    runtime.ready_clients["@STORAGE"] = storage_client


def main():
    """Start the dataClay server (Execution Environment).

    Keep in mind that the configuration in both dataClay's global ConfigOptions
    and the server-specific one called ServerConfigOptions should be accurate.
    Furthermore, this function expects that the caller will take care of the
    dataClay library initialization.

    This function does not return (by itself), so feel free to spawn it inside
    a greenlet or a subprocess (typical in testing)
    """
    set_defaults()

    runtime.establish(RuntimeType.exe_env, {
        'get_object_by_id': get_object_by_id,
        'get_execution_environment_by_oid': get_execution_environment_by_oid,
        'new_instance': new_instance,
        'make_persistent': make_persistent,
        'store_object': store_object,
        'execute_implementation_aux': execute_implementation_aux,
        'move_object': move_object,
    })

    # Create the deployment folder and add it to the path
    try:
        os.makedirs(settings.deploy_path_source)
    except OSError as e:
        if e.errno != 17:
            # Not the "File exists" expected error, reraise it
            raise
    sys.path.insert(1, settings.deploy_path_source)

    # logger.debug("Current sys.path: %s", sys.path)

    logger.info("Starting DataServiceEE on %s:%d", settings.server_listen_addr,
                settings.server_listen_port)

    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1000),
                             options=(('grpc.max_send_message_length', 1000 * 1024 * 1024,),
                                      ('grpc.max_receive_message_length', 1000 * 1024 * 1024,),))
    except Exception as e:
        logger.debug("grpc.server call exception:\n%s", e)
    
    ee = DataServiceEE()
    ds.add_DataServiceServicer_to_server(ee, server)

    address = str(settings.server_listen_addr) + ":" + str(settings.server_listen_port)

    # ToDo: Better way for start server?
    server.add_insecure_port(address)
    server.start()
    local_ip = preface_autoregister()
    start_autoregister(local_ip)
    ee.ass_client()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except RuntimeError:
        logger.info("Runtime Error")
        return
    finally:
        server.stop(0)
