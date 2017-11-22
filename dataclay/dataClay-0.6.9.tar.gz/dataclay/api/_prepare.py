"""Initialization and finalization of dataClay client API.

The `init` and `finish` functions are availble through the
dataclay.api package.
"""

from communication.grpc.clients.ee_client import EEClient

from dataclay import runtime
from dataclay.conf import settings
from dataclay.core.constants import lang_codes
from dataclay.managers.classes import ExecutionGateway, UserType
from dataclay.managers.objects.deserialization import deserialize_return
from dataclay.managers.objects.serialization import serialize_params_or_return, serialize_dcobj_with_data
from dataclay.runtime_classes import RuntimeType

import importlib
import logging
import lru
import random
import uuid
from weakref import WeakValueDictionary

# Sentinel-like object to catch some typical mistakes
UNDEFINED_LOCAL = object()

logger = logging.getLogger('dataclay.api')

__all__ = ("get_object_by_id", "get_execution_environment_by_oid",
           "store_object", "make_persistent",
           "new_instance", "get_execution_environments_info",
           "execute_implementation_aux", "get_by_alias",
           "delete_alias", "move_object")

alias_cache = lru.LRU(50)


def get_object_by_id(self, object_id):
    # Note that this method requires several calls to the LogicModule
    # (getObjectInfo). If the class_id is available, like the typical response
    # or parameter serialization, it is better to use the new_instance method.
    try:
        return self.inmemory_objects[object_id]
    except KeyError:
        pass

    full_name, namespace = self.ready_clients["@LM"].get_object_info(
        settings.current_session_id, object_id)
    logger.debug("Trying to import full_name: %s from namespace %s",
                 full_name, namespace)

    # Rearrange the division, full_name may include dots (and be nested)
    prefix, class_name = ("%s.%s" % (namespace, full_name)).rsplit('.', 1)
    m = importlib.import_module(prefix)
    klass = getattr(m, class_name)

    dataset_id = self.ready_clients["@LM"].get_object_dataset_id(
        settings.current_session_id, object_id)

    o = self.new_instance(klass._dclay_class_extradata.class_id,
                          persistent_flag=True,
                          loaded_flag=False,
                          proxy_flag=False,
                          execenv_id=None,
                          dataset_id=dataset_id,
                          object_id=object_id)
    self.inmemory_objects[object_id] = o
    return o


def get_execution_environment_by_oid(self, object_id):
    metadata = self.ready_clients["@LM"].get_metadata_by_oid(
        settings.current_session_id, object_id)

    logger.debug("Received the following MetaDataInfo for object %s: %s",
                 object_id, metadata)
    return iter(metadata.locations).next()


def get_all_execution_environments_by_oid(self, object_id):
    metadata = self.ready_clients["@LM"].get_metadata_by_oid(
        settings.current_session_id, object_id)

    logger.debug("Received the following MetaDataInfo for object %s: %s",
                 object_id, metadata)
    return metadata.locations


def get_execution_environments_info(self):
    return self.ready_clients["@LM"].get_execution_environments_info(settings.current_session_id,
                                                                     lang_codes.LANG_PYTHON)


# ToDo: Correct the hint use
def get_by_alias(self, dclay_cls, alias):
    class_id = dclay_cls._dclay_class_extradata.class_id

    oid, hint = self.ready_clients["@LM"].get_object_from_alias(
        settings.current_session_id, class_id, alias)

    return self.new_instance(
        class_id,
        object_id=oid,
        loaded_flag=False,
        proxy_flag=True,
        persistent_flag=True,
    )


def delete_alias(self, dclay_cls, alias):
    class_id = dclay_cls._dclay_class_extradata.class_id

    self.ready_clients["@LM"].delete_alias(settings.current_session_id, class_id, alias)


def store_object(self, instance):
    raise RuntimeError("StoreObject can only be used from the ExecutionEnvironment")


def move_object(self, instance, source_backend_id, dest_backend_id):
    client = self.ready_clients["@LM"]
    logger.debug("Moving object %r from %s to %s",
                 instance, source_backend_id, dest_backend_id)

    dco_extradata = instance._dclay_instance_extradata
    object_id = dco_extradata.object_id

    client.move_objects(settings.current_session_id, object_id,
                        source_backend_id, dest_backend_id)


def make_persistent(self, instance, alias, backend_id, recursive):
    client = self.ready_clients["@LM"]
    logger.debug("Starting make persistent object")

    only_register = False

    if instance.is_persistent():
        # ToDo: Need to check if isPendingToRegister?
        if runtime.current_type == RuntimeType.exe_env:
            only_register = True
            logger.debug("Object need to be only registered")
        else:
            logger.verbose("Trying to make persistent %r, which already is persistent. Ignoring", self)
            return

    instance._dclay_instance_extradata.persistent_flag = True

    if backend_id is UNDEFINED_LOCAL:
        # This is a common end user pitfall,
        # @abarcelo thinks that it is nice
        # (and exceptionally detailed) error
        raise RuntimeError("""
You are trying to use dataclay.api.LOCAL but either:
  - dataClay has not been initialized properly
  - LOCAL has been wrongly imported.

Be sure to use LOCAL with:

from dataclay import api

and reference it with `api.LOCAL`

Refusing the temptation to guess.""")

    if backend_id is None:
        # If no execution environment specified select it randomly
        backend_id = random.choice(self.get_execution_environments_info().keys())

    logger.verbose("ExecutionEnvironment chosen for MakePersistent is: %s", backend_id)

    # ToDo: retrieve it with dest_ee_id??
    hint = instance._dclay_instance_extradata.execenv_id

    pending_objs = list()
    pending_objs.append(instance)
    obs_to_register = dict()
    serialized_objs = list()
    objs_already_persistent = set()
    ignore_user_types = False  # FIXME
    datasets_specified = dict()
    reg_infos = list()

    while pending_objs:
        current_obj = pending_objs.pop()

        dco_extradata = current_obj._dclay_instance_extradata
        object_id = dco_extradata.object_id
        dataset_id = dco_extradata.dataset_id

        dcc_extradata = current_obj._dclay_class_extradata
        class_id = dcc_extradata.class_id

        if class_id is None:
            raise RuntimeError("ClassID is None. Stubs are not used properly.")

        if only_register and runtime.current_type == RuntimeType.exe_env:
            infos = [object_id, class_id,
                     settings.current_session_id, dataset_id]
            reg_infos.append(infos)

        # Ignore proxies or already persistent objects
        #if current_obj.is_persistent() or current_obj.is_proxy() \
        #        or object_id in objs_already_persistent:
        #    continue

        # ToDo: Check it
        # This object will soon be persistent
        # dco_extradata.persistent_flag = True
        dco_extradata.loaded_flag = False

        # First store since others OIDs are recursively created while creating MetaData
        if not object_id:
            object_id = uuid.uuid4()
            dco_extradata.object_id = object_id

        # Store dataset id in the datasets dict
        if dataset_id is not None:
            datasets_specified[object_id] = dataset_id
        else:
            # And assume that it will be put to the dataset_for_store accordingly to the session
            dataset_id = client.get_dataset_id(settings.current_id,
                                               settings.current_credential,
                                               settings.dataset_for_store)
            datasets_specified[object_id] = dataset_id
            
        objs_already_persistent.add(object_id)
        obs_to_register[object_id] = class_id

        # Serialize the objects to make persistent
        serialized_objs.append(
            serialize_dcobj_with_data(current_obj, pending_objs,
                                      ignore_user_types, hint)
        )

        infos = [object_id, class_id,
                 settings.current_session_id, dataset_id]

        if infos not in reg_infos:
            reg_infos.append(infos)

    # Cache the (object_id, hint) tuple with alias as key
    object_id_to_have_alias = None
    if alias is not None:
        object_id_to_have_alias = instance._dclay_instance_extradata.object_id
        logger.debug("Adding to cache object with alias %s and oid %s",
                     alias, object_id_to_have_alias)
        alias_cache[alias] = (object_id_to_have_alias, hint)

    if only_register:
        objs_to_register = list()
        for reg_info in serialized_objs:
            objs_to_register.append(reg_info)
        logger.debug("Registering objects %s", objs_to_register)

        client.register_objects(reg_infos, backend_id,
                                object_id_to_have_alias, alias,
                                lang_codes.LANG_PYTHON)

        for reg_obj in reg_infos:
            # ToDo: Correct it
            # obj = runtime.get_object_by_id(oid)
            if reg_obj[0] is instance._dclay_instance_extradata.object_id:
                instance._dclay_instance_extradata.persistent_flag = True

    else:

        objs_to_register = list()
        for reg_info in serialized_objs:
            objs_to_register.append(reg_info)

        if alias is not None:
            logger.debug("Making persistent object %s with alias %s and associated objects: %s",
                         instance._dclay_instance_extradata.object_id,
                         alias, objs_to_register)

        else:
            logger.debug("Making persistent object %s and associated objects: %s",
                         instance._dclay_instance_extradata.object_id,
                         objs_to_register)

        for reg_obj in serialized_objs:
            # ToDo: Correct it
            # obj = runtime.get_object_by_id(reg_obj[0])
            if reg_obj[0] is instance._dclay_instance_extradata.object_id:
                instance._dclay_instance_extradata.persistent_flag = True

        if recursive:
            for name, property in instance._dclay_class_extradata.properties.iteritems():
                attribute = object.__getattribute__(instance, "_dataclay_property_" + name)
                if isinstance(property.type, UserType) and attribute is not None:
                    attribute.make_persistent()

        client.make_persistent(session_id=settings.current_session_id,
                               dest_backend_id=backend_id,
                               serialized_objects=serialized_objs,
                               ds_specified=datasets_specified,
                               object_to_have_alias=object_id_to_have_alias,
                               alias=alias)

def new_instance(self, class_id, **kwargs):
    logger.verbose("Creating an instance from the class: {%s}", class_id)

    try:
        # Note that full_class_name *includes* namespace (Python-specific behaviour)
        full_class_name = self.local_available_classes[class_id]
    except KeyError:
        raise RuntimeError("Class {%s} is not amongst the locally available classes, "
                           "check contracts and/or initialization" % class_id)

    package_name, class_name = full_class_name.rsplit(".", 1)
    m = importlib.import_module(package_name)
    klass = getattr(m, class_name)

    return ExecutionGateway.new_dataclay_instance(klass, **kwargs)


def execute_implementation_aux(self, operation_name, instance, parameters):
    stub_info = instance._dclay_class_extradata.stub_info
        
    implementation_stub_infos = stub_info.implementations

    object_id = instance._dclay_instance_extradata.object_id
    
    logger.verbose("Calling operation named '%s'", operation_name)
    logger.debug("Call is being done into %r with #%d parameters",
                 instance, len(parameters))

    serialized_params = serialize_params_or_return(
        params=parameters,
        iface_bitmaps=None,
        params_spec=implementation_stub_infos[operation_name].parameters,
        params_order=implementation_stub_infos[operation_name].paramsOrder)

    remote_impl = [implementation_stub_infos[operation_name].remoteImplID,
                   implementation_stub_infos[operation_name].contractID,
                   implementation_stub_infos[operation_name].interfaceID]

    md_info = runtime.ready_clients["@LM"].get_metadata_by_oid(settings.current_session_id, object_id)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("MetaDataInfo received for object: %s", object_id)
        logger.debug(" - ExecutionEnvironments for previous object: %s", md_info.locations)

    # ToDo: Check it with the replicas
    for exeenv_id, exeenv in md_info.locations.iteritems():

        try:
            execution_client = self.ready_clients[exeenv_id]
        except KeyError:

            logger.verbose("Not found Client to ExecutionEnvironment {%s}! Starting it at %s:%d",
                           exeenv_id, exeenv.hostname, exeenv.port)

            execution_client = EEClient(exeenv.hostname, exeenv.port)
            self.ready_clients[exeenv_id] = execution_client

        ret = execution_client.ds_execute_implementation(
            object_id,
            remote_impl[0],
            settings.current_session_id,
            serialized_params)

        break

    logger.verbose("Result of operation named '%s' received", operation_name)

    if ret is None:
        return None
    else:
        return deserialize_return(ret,
                                  None,
                                  implementation_stub_infos[operation_name].returnType,
                                  WeakValueDictionary())
