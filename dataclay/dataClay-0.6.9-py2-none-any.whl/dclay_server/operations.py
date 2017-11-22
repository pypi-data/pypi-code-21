from io import BytesIO
import logging
import lru
import yaml
from threading import local

from dataclay import runtime
from dataclay.core import constants
from dataclay.core.constants import lang_codes
from dataclay.core.paraver import trace_function
from dataclay.core.network.exceptions import ClientError
from dataclay.managers import metaclass_containers
from dataclay.managers.classes import properties
from dataclay.managers.classes.filesystem import deploy_class
from dataclay.conf import settings
from dataclay.managers.objects import cached_objects_dict
from dataclay.managers.objects.deserialization import deserialize_dataclayobject_for_get, deserialize_params
from dataclay.managers.objects.serialization import serialize_params_or_return

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

# This variable will store the following:
#   - iface_bm (Interface BitMap): used across calls
#   - session_id (SessionID): is maintained during a deep call
#   - dataset_id (DataSetID): set on executeImplementation and newPersistentInstance,
#                             and used for makePersistent of instances.
thread_local_info = local()

# FIXME de-hardcode this value
cached_metadatainfo = lru.LRU(50)
cached_sessioninfo = lru.LRU(50)


@trace_function
def ds_deploy_classes(payload):
    """Deploy Classes (execution stubs) to the Python Execution Environment.

    This function is not used by the Python execution environment. This function
    raises an exception.

    :param payload: The bytearray containing the payload of this RPC.
    :return: The response (empty string)
    """
    logger.debug("Attending DS_DEPLOY_CLASSES call --not supported")
    raise ClientError(constants.error_codes.CLASS_UNSUPPORTED_LANGUAGE,
                      "Method 'deploy_classes' not supported in Python Execution Environment")


@trace_function
def ds_deploy_metaclasses(namespace, classes_map_yamls):
    """Deploy MetaClass containers to the Python Execution Environment.

    This function stores in a file all the MetaClass, in addition to (optionally)
    putting them into the cache, according to the ConfigOptions.

    :param namespace: The namespace 
    :param classes_map: classes map
    :return: The response (empty string)
    """
    for class_name, clazz_yaml in classes_map_yamls.iteritems():
        metaclass = yaml.load(clazz_yaml)
        metaclass_containers.deploy_metaclass_grpc(
            namespace, class_name, clazz_yaml, metaclass)

        if metaclass.name == "UserType" or metaclass.name == "HashType":
            # logger.warning("Ignoring %s dataClay MetaClass" % metaclass.name)
            # logger.debug(metaclass)
            continue

        if metaclass.name == "DataClayPersistentObject" \
                or metaclass.name == "DataClayObject"\
                or metaclass.name == "StorageObject":
            continue

        # logger.info("Deploying class %s to deployment source path %s",
        #             metaclass.name, settings.deploy_path_source)

        try:
            # ToDo: check whether `lang_codes.LANG_PYTHON` or `'LANG_PYTHON'` is the correct key here
            import_lines = metaclass.languageDepInfos[lang_codes.LANG_PYTHON].imports
            imports = "\n".join(import_lines)
        except KeyError:
            # What is most likely is languageDepInfos not having the Python
            imports = ""

        deploy_class(metaclass.namespace, metaclass.name,
                     metaclass.juxtapose_code(True),
                     imports,
                     settings.deploy_path_source,
                     ds_deploy=True)
        # logger.debug("Deployment of class %s successful", metaclass.name)

    return str()


def get_object_metadatainfo(object_id):
    """Get the MetaDataInfo for a certain object.
    :param object_id: The ID of the persistent object
    :return: The MetaDataInfo for the given object.

    If we have it available in the cache, return it. Otherwise, call the
    LogicModule for it.
    """
    logger.info("Getting MetaData for object {%s}", object_id)

    try:
        md_info = cached_metadatainfo[object_id]
        logger.debug("Hit on cached_metadatainfo")
    except KeyError:
        md_info = runtime.ready_clients["@LM"].get_metadata_by_oid(thread_local_info.session_id, object_id)
        cached_metadatainfo[object_id] = md_info
    return md_info


def get_local_instance(session_id, object_id):
    # Load the object dictionary, cache or from the Storage Location
    try:
        py_object = cached_objects_dict[object_id]
        logger.debug("Hit on cached_objects_dict")
    except KeyError:
        logger.debug("Cache for OID = %s failed", object_id)

        objs_with_data = runtime.ready_clients["@STORAGE"].ds_get_objects(session_id, [object_id], True, False)

        py_object = None
        for obj_with_data in objs_with_data:
            
            obj_oid = obj_with_data[0]
            obj_class_id = obj_with_data[1]
            obj_metadata = obj_with_data[2]
            objbytes = obj_with_data[3]
            if obj_oid != object_id:
                logger.debug("Expected ObjectID {%s} and received {%s}", object_id, obj_oid)
                raise NotImplementedError("Complex objects (= with relations) are not supported yet")
            temp_object = deserialize_dataclayobject_for_get(obj_oid, obj_class_id, obj_metadata, BytesIO(objbytes), dict())
            cached_objects_dict[obj_oid] = temp_object
            if obj_oid == object_id:
                py_object = temp_object

        assert py_object is not None, \
            "One of the entries in the dictionary should be the asked object"
    return py_object


def internal_exec_impl(implementation_name, instance, params):
    """Internal (network-agnostic) execute implementation behaviour.

    :param instance: The object in which execution will be performed.
    :param implementation_name: Name of the implementation (may also be some dataClay specific $$get*
    :param params: The parameters (args)
    :return: The return value of the function being executed.
    """
    if implementation_name.startswith(properties.DCLAY_GETTER_PREFIX):
        prop_name = implementation_name[len(properties.DCLAY_GETTER_PREFIX):]
        ret_value = getattr(instance, properties.DCLAY_PROPERTY_PREFIX + prop_name)
        logger.debug("Getter: for property %s returned %r", prop_name, ret_value)

    elif implementation_name.startswith(properties.DCLAY_SETTER_PREFIX):
        prop_name = implementation_name[len(properties.DCLAY_SETTER_PREFIX):]
        logger.debug("Setter: for property %s (value: %r)", prop_name, params[0])
        setattr(instance, properties.DCLAY_PROPERTY_PREFIX + prop_name, params[0])
        ret_value = None

    else:
        logger.debug("Call: %s(*args=%s)", implementation_name, params)
        dataclay_decorated_func = getattr(instance, implementation_name)
        ret_value = dataclay_decorated_func._dclay_entrypoint(instance, *params)

    return ret_value


def set_local_session_and_dataset(session_id):
    """Set the global `thread_local_info` with Session and DataSet data.

    :param session_id: The UUID for SessionID.
    :return: None

    Set both the SessionID (just as provided) and also the DataSetID associated
    to that Session. Note that the cache is used (`cached_sessioninfo`) when
    available. If not in the cache, perform a getInfoOfSessionForDS RPC call.
    """
    try:
        session_info_entry = cached_sessioninfo[session_id]
    except KeyError:
        session_info_entry = runtime.ready_clients["@LM"].get_info_of_session_for_ds(session_id)
        cached_sessioninfo[session_id] = session_info_entry

    thread_local_info.session_id = session_id
    thread_local_info.dataset_id = session_info_entry[0][0]




@trace_function
def ds_exec_impl(object_id, implementation_id, serialized_params_grpc_msg, session_id):
    """Perform a Remote Execute Implementation.

    See Java Implementation for details on parameters and purpose.
    """

    set_local_session_and_dataset(session_id)
    logger.debug("Starting new execution")
    logger.debug("SessionID of current execution: %s", session_id)
    logger.debug("ObjectID of current execution: %s", object_id)
    logger.debug("ImplementationID in which the method belongs: %s", implementation_id)

    instance = get_local_instance(session_id, object_id)

    metaclass_container = instance._dclay_class_extradata.metaclass_container
    operation = metaclass_container.get_operation(implementation_id)
    logger.debug("DESERIALIZING PARAMETERS")

    num_params = serialized_params_grpc_msg[0]
    params = [] 
    if num_params > 0:
        params = deserialize_params(serialized_params_grpc_msg, None,
                                    operation.params,
                                    operation.paramOrder,
                                    dict())
    logger.debug("STARTING EXECUTION")

    ret_value = internal_exec_impl(operation.name,
                                   instance,
                                   params)
    
    logger.debug("SERIALIZING RESULT ")
    if ret_value is None:
        logger.debug(" -> Returning None")
        return None
    
    logger.debug(" -> Serializing %s (type: %s)", ret_value, operation.returnType)
    return serialize_params_or_return({0: ret_value}, 
                                      None, 
                                      {"0": operation.returnType},
                                      ["0"])

@trace_function
def new_persistent_instance(payload):
    """Create, make persistent and return an instance for a certain class."""

    raise NotImplementedError("NewPersistentInstance RPC is not yet ready (@ Python ExecutionEnvironment)")
