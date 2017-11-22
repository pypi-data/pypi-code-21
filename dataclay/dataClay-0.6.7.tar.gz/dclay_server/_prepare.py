from communication.grpc.clients.ee_client import EEClient
import dataclay
from dataclay.conf import settings
from dataclay.core.constants import lang_codes
from dataclay.core.paraver import trace_function
from dataclay.managers.classes import ExecutionGateway
from dataclay.managers.metaclass_containers import load_metaclass_info
from dataclay.managers.objects import cached_objects_dict
from dataclay.managers.objects.deserialization import deserialize_return
from dataclay.managers.objects.serialization import serialize_dcobj_with_data, serialize_params_or_return
import importlib
import logging
import lru
import traceback
import uuid
from weakref import WeakValueDictionary

from . import operations


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

__all__ = ("get_object_by_id", "get_execution_environment_by_oid",
           "store_object", "make_persistent", "new_instance",
           "execute_implementation_aux", "move_object")

logger = logging.getLogger(__name__)
alias_cache = lru.LRU(50)


@trace_function
def store_object(self, instance):
    if not instance.is_persistent():
        raise RuntimeError("StoreObject should only be called on Persistent Objects. "
                           "Ensure to call make_persistent first")

    internal_store(instance, make_persistent=False)


# FixMe: For the moment is not updated
@trace_function
def make_persistent(self, instance, alias, dest_ee_id, recursive):
    if instance.is_persistent():
        logger.verbose("Trying to make persistent %r, which already is persistent. Ignoring", self)
        return

    # TODO: add support for that:
    if alias is not None:
        logger.warning("Server-side make_persistent with alias is not supported. Ignoring.")

    # TODO: add support for that:
    if dest_ee_id is not None:
        logger.warning("Server-side EE pinning on make_persistent is not supported. Ignoring.")

    internal_store(instance, make_persistent=True)


@trace_function
def get_object_by_id(self, object_id):
    """Obtain a (thin) PersistentObject from the ObjectID
    :param object_id: The UUID of the Object
    :return: An Execution Class instance, typically with
    ExecuteRemoteImplementation as True
    """
    """
    try:
        return self.inmemory_objects[object_id]
    except KeyError:
        pass

    logger.info("Building ObjectID {%s}", object_id)

    # Get the class
    md_info = self.ready_clients["@LM"].get_object_info(operations.thread_local_info.session_id, object_id)
    logger.debug("MetaclassID: {%s}", md_info.metaclass_id)

    o = self.new_instance(md_info.metaclass_id,
                          persistent_flag=True,
                          loaded_flag=False,
                          dataset_id=md_info.dataset_id,
                          proxy_flag=False,
                          object_id=object_id)
    self.inmemory_objects[object_id] = o
    """
    o = operations.get_local_instance(operations.thread_local_info.session_id, object_id)

    return o


def get_execution_environment_by_oid(self, object_id):
    # TODO: perform some cache on that, or use the local StorageLocation's cache
    metadata = self.ready_clients["@LM"].get_metadata_by_oid(
        operations.thread_local_info.session_id, object_id)

    logger.debug("Received the following MetaDataInfo for object %s: %s",
                 object_id, metadata)
    return iter(metadata.locations).next()


def get_all_execution_environments_by_oid(self, object_id):
    # TODO: perform some cache on that, or use the local StorageLocation's cache
    metadata = self.ready_clients["@LM"].get_metadata_by_oid(
        operations.thread_local_info.session_id, object_id)

    logger.debug("Received the following MetaDataInfo for object %s: %s",
                 object_id, metadata)
    return metadata.locations


def new_instance(self, class_id, **kwargs):
    logger.info("Creating an instance from the class: {%s}", class_id)

    # Obtain the class name from the MetaClassInfo
    full_class_name, namespace = load_metaclass_info(class_id)
    logger.debug("MetaClassID {%s}: full class name `%s` | namespace `%s`" % 
                 (class_id, full_class_name, namespace))

    class_name_parts = full_class_name.rsplit(".", 1)

    if len(class_name_parts) == 2:
        package_name, class_name = class_name_parts
        module_name = "%s.%s" % (namespace, package_name)
    else:
        class_name = class_name_parts[0]
        module_name = "%s" % namespace

    try:
        m = importlib.import_module(module_name)
    except ImportError:
        logger.error("new_instance failed due to ImportError")
        logger.error("load_metaclass_info returned: full_class_name=%s, namespace=%s",
                     full_class_name, namespace)
        logger.error("Trying to import: %s", module_name)

        if logger.isEnabledFor(logging.DEBUG):
            logger.error("DEBUG: Stacktrace for the error:\n%s",
                         traceback.format_exc())

        # # Very ugly, but required for some deep debugging strange behaviour
        # import sys
        # logger.error("The import path is: %s", sys.path)
        #
        # import subprocess
        # logger.error("`ls -laR %s` yields the following:\n%s",
        #              settings.deploy_path_source,
        #              subprocess.check_output("ls -laR %s" % settings.deploy_path_source,
        #                                      shell=True)
        #              )

        # Let the exception raise again, untouched
        raise

    klass = getattr(m, class_name)

    return ExecutionGateway.new_dataclay_instance(klass, **kwargs)


def move_object(self, instance, source_backend_id, dest_backend_id):
    client = self.ready_clients["@LM"]
    logger.debug("Moving object %r from %s to %s",
                 instance, source_backend_id, dest_backend_id)

    dco_extradata = instance._dclay_instance_extradata
    object_id = dco_extradata.object_id

    client.move_objects(operations.thread_local_info.session_id,
                        object_id, source_backend_id, dest_backend_id)


def execute_implementation_aux(self, operation_name, instance, parameters):
    dco_extradata = instance._dclay_instance_extradata
    if dco_extradata.loaded_flag:
        # Client
        raise RuntimeError("Execute Implementation Aux runtime helper should only be called for non-loaded")

    object_id = dco_extradata.object_id
    md_info = operations.get_object_metadatainfo(object_id)

    if settings.environment_id in md_info.locations:
        logger.debug("Object execution is local")

        # Note that fat_instance tend to be the same as instance...
        # *except* if it is a proxy
        fat_instance = operations.get_local_instance(operations.thread_local_info.session_id, object_id)
        return operations.internal_exec_impl(operation_name, fat_instance, parameters)
    else:
        logger.debug("Object execution is not local")

        for exeenv_id, exeenv in md_info.environments.iteritems():

            dcc_extradata = instance._dclay_class_extradata
            metaclass_container = dcc_extradata.metaclass_container
            # iface_bm = operations.thread_local_info.iface_bm
            operation = metaclass_container.get_operation_from_name(operation_name)

            serialized_params = serialize_params_or_return(
                parameters, None, operation.params, operation.paramOrder
            )

            logger.info("Calling to ExecutionEnvironment {%s}", exeenv_id)
            try:
                execution_client = self.ready_clients[exeenv_id]
            except KeyError:
                execution_client = EEClient(exeenv.hostname, exeenv.port)
                self.ready_clients[exeenv_id] = execution_client

            ret = execution_client.ds_execute_implementation(
                object_id,
                operation.implementations[0].dataClayID,
                operations.thread_local_info.session_id,
                serialized_params)

            if ret is None:
                return None
            else:
                return deserialize_return(ret,
                                          None,
                                          operation.returnType,
                                          WeakValueDictionary())


#########################################
# Helper functions, not runtime methods #
#########################################

def internal_store(instance, make_persistent=True):
    """Perform the storage (StoreObject call) for an instance.

    :param instance: The DataClayObject willing to be stored.
    :param make_persistent: Flag, True when DS_STORE_OBJECT should be called
    and False when DS_UPSERT_OBJECT is the method to be called.
    :return: A dictionary containing the classes for all stored objects.

    This function works for two main scenarios: the makePersistent one (in
    which the instance is not yet persistent) and the update (in which the
    instance is persistent).

    The return dictionary is the same in both cases, but note that the update
    should not use the provided instance for updating metadata to the LM.
    """
    client = dataclay.runtime.ready_clients["@STORAGE"]

    pending_objs = [instance]
    stored_objects_classes = dict()
    serialized_objs = list()

    while pending_objs:
        current_obj = pending_objs.pop()

        # Ignore proxies or already persistent objects
        if (current_obj.is_persistent() or current_obj.is_proxy()) and make_persistent:
            continue

        dco_extradata = current_obj._dclay_instance_extradata
        dcc_extradata = current_obj._dclay_class_extradata
        object_id = dco_extradata.object_id

        # This object will soon be persistent
        dco_extradata.persistent_flag = True
        # Just in case (should have been loaded already)
        dco_extradata.loaded_flag = True

        # First store since others OIDs are recursively created while creating MetaData
        if not object_id:
            assert make_persistent  # makes no sense to enter here in non-make_persistent scenarios
            object_id = uuid.uuid4()
            dco_extradata.object_id = object_id
            dco_extradata.dataset_id = operations.thread_local_info.dataset_id

        # The object is inmemory and now it can be cached
        dataclay.runtime.inmemory_objects[object_id] = current_obj
        cached_objects_dict[object_id] = current_obj

        logger.debug("Ready to make persistent object {%s} of class %s {%s}" % 
                     (object_id, dcc_extradata.classname, dcc_extradata.class_id))

        stored_objects_classes[object_id] = dcc_extradata.class_id

        # If we are not in a make_persistent, the dataset_id hint is null (?)
        serialized_objs.append(serialize_dcobj_with_data(
            current_obj, pending_objs, False, None))

    if make_persistent:
        
        # TODO make some cache or something more intelligent here
        dataset_id = operations.thread_local_info.dataset_id if make_persistent else None
        reg_infos = list()
        dcc_extradata = current_obj._dclay_class_extradata
        infos = [object_id, dcc_extradata.class_id,
                 operations.thread_local_info.session_id, dataset_id]
        reg_infos.append(infos)
    
        lm_client = dataclay.runtime.ready_clients["@LM"]

        lm_client.register_objects(reg_infos, settings.environment_id, None, None,
                                   lang_codes.LANG_PYTHON)
        client.ds_store_objects(operations.thread_local_info.session_id, serialized_objs, False, None)
    else:
        client.ds_upsert_objects(operations.thread_local_info.session_id, serialized_objs)
