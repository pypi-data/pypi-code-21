"""Deserialization code related to DataClay objects

The code implemented in this module is (at "this moment") identical to the ones
implemented in the Java package client.CommonLib. Specifically, the deserialize*
functions are more or less adapted here.
"""

import logging
from io import BytesIO

from dataclay import runtime
from dataclay.core.containers import DataClayObjectMetaData
from dataclay.core.exceptions import InvalidPythonSignature
from dataclay.core.management.classmgr import serialization_types
from dataclay.core.primitives import *
from dataclay.runtime_classes import RuntimeType

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


def deserialize_association(
        io_file,  # final DataClayByteBuffer
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        objects_map,  # Map<ObjectID, Reference<DataClayObject>>
        # in Python, objects_map is expected to be a WeakValueDictionary
        metadata,  # final DataClayObjectMetaData
        # the_ds_ref --unused `final DataServiceAPI`
        cur_deserialized_objs,  # final Map<Integer, Object>
):
    tag = Vlq().read(io_file)
    logger.info("Deserializing association for tag: %d", tag)

    object_id = metadata[0][tag]
    metaclass_id = metadata[1][tag]

    try:
        obj = objects_map[object_id]
        logger.debug("Hit of ObjectID: {%s} on the object map", object_id)
    except KeyError:
        logger.debug("Miss for ObjectID: {%s}, not present in objects map",
                         object_id)
        try:
            obj = runtime.inmemory_objects[object_id]
        except KeyError:
            obj = runtime.new_instance(metaclass_id,
                                        persistent_flag=True,
                                        loaded_flag=False,
                                        proxy_flag=False,
                                        object_id=object_id)
            runtime.inmemory_objects[object_id] = obj
        objects_map[object_id] = obj

    cur_deserialized_objs[tag] = obj
    return obj


def deserialize_params(
        serialized_params_or_return,  # Map<Integer, Tuple<ObjectID, byte[]>>
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        param_specs,  # Map<String, Type>
        params_order,  # List<String>
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
):
    return deserialize_params_or_return(serialized_params_or_return,
                        iface_bitmaps,
                        param_specs,
                        params_order,
                        objects_map)
    
def deserialize_return(
        serialized_params_or_return,  # Map<Integer, Tuple<ObjectID, byte[]>>
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        return_type,  # Map<String, Type>
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
):
    
    if serialized_params_or_return[0] == 0:
        return None 
    return deserialize_params_or_return(serialized_params_or_return,
                        iface_bitmaps,
                        {"0": return_type},
                        ["0"],
                        objects_map)[0]


def deserialize_params_or_return(
        serialized_params_or_return,  # Map<Integer, Tuple<ObjectID, byte[]>>
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        param_specs,  # Map<String, Type>
        params_order,  # List<String>
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
):
    num_params = serialized_params_or_return[0]
    params = [None] * num_params

    # objects_map is a WeakValueDictionary, we need something a little bit more
    # resistent to garbage collector action
    retain_those_objects = list()

    #### IMMUTABLES todo: change deserialize_any #####
    for i, serialized_param in serialized_params_or_return[1].iteritems():

        ser = BytesIO(serialized_param)
        if i < num_params:
            params[i] = deserialize_immutable(ser, param_specs[params_order[i]])
        else:
            retain_those_objects.append(deserialize_immutable(ser, param_specs[params_order[i]]))
    
    #### LANGUAGE todo: change deserialize_any #####
    for i, serialized_param in serialized_params_or_return[2].iteritems():

        ser = BytesIO(serialized_param[1])

        if i < num_params:
            params[i] = deserialize_language(ser, param_specs[params_order[i]])
        else:
            retain_those_objects.append(deserialize_language(ser, param_specs[params_order[i]]))   
                 
    #### VOLATILE todo: change deserialize_any #####
    for i, serialized_param in serialized_params_or_return[3].iteritems():

        object_id = serialized_param[0]
        class_id = serialized_param[1]
        metadata = serialized_param[2]
        ser = BytesIO(serialized_param[3])

        if i < num_params:
            params[i] = deserialize_obj_with_data(
                object_id, class_id, metadata,
                ser, iface_bitmaps, objects_map)
        else:
            retain_those_objects.append(deserialize_obj_with_data(
                object_id, class_id, metadata,
                ser, iface_bitmaps, objects_map))
    
    #### PERSISTENT todo: change deserialize_any #####
    for i, serialized_param in serialized_params_or_return[4].iteritems():

        object_id = serialized_param[0]
        class_id = serialized_param[2]
        if i < num_params:
            params[i] = deserialize_persistent(object_id, class_id, objects_map)
        else:
            retain_those_objects.append(deserialize_persistent(object_id, class_id, objects_map))        
                    
                   
            
    return params

def deserialize_dataclayobject_for_get(
        object_id,
        object_class_id, 
        metadata,
        io_file,  # final DataClayByteBuffer
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
        # in Python, objects_map is expected to be a WeakValueDictionary
):
    # Format: [ DATA ]
    try:
        instance = runtime.inmemory_objects[object_id]
        is_loaded = instance._dclay_instance_extradata.loaded_flag
    except KeyError:
        instance = runtime.new_instance(
            object_class_id, object_id=object_id, persistent_flag=True,
            loaded_flag=False, proxy_flag=False)
        runtime.inmemory_objects[object_id] = instance
        is_loaded = False

    # This is safe because the value is weakreferenced
    objects_map[object_id] = instance

    if not is_loaded:
        cur_deser_python_objs = dict()
        instance.deserialize(io_file, None, objects_map, metadata, cur_deser_python_objs)
        instance._dclay_instance_extradata.loaded_flag = True

    return instance

def deserialize_obj_with_data(
        object_id, 
        class_id, 
        metadata,
        io_file,  # final DataClayByteBuffer
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
):

    try:
        obj = objects_map[object_id]
        logger.debug("Hit of ObjectID: {%s} on the object map", object_id)
    except KeyError:
        logger.debug("Miss for ObjectID: {%s}, not present in objects map",
                         object_id)
        try:
            obj = runtime.inmemory_objects[object_id]
        except KeyError:
            obj = runtime.new_instance(class_id,
                                        persistent_flag=True,
                                        loaded_flag=False,
                                        proxy_flag=False,
                                        object_id=object_id)
            runtime.inmemory_objects[object_id] = obj
        objects_map[object_id] = obj

    obj.deserialize(io_file, iface_bitmaps, objects_map, metadata, dict())
    obj._dclay_instance_extradata.loaded_flag = True
    if runtime.current_type == RuntimeType.exe_env:
        # TODO: store this ExecutionEnvironmentID in the object...
        #obj._dclay_instance_extradata.execenv_id =
        pass

    return obj


def deserialize_immutable(
        io_file,
        type_, 
):
    # Well, if it is a primitive type we already have them...
    try:
        ptw = PyTypeWildcard(type_.signature)
    except InvalidPythonSignature:
        raise NotImplementedError("Only Java primitive types are "
                                      "understood in Python.")
    return ptw.read(io_file)

def deserialize_language(
        io_file,
        type_, 
):
    # Well, if it is a primitive type we already have them...
    try:
        ptw = PyTypeWildcard(type_.signature)
    except InvalidPythonSignature:
        raise NotImplementedError("In fact, InvalidPythonSignature was "
                                      "not even implemented, seems somebody is "
                                      "raising it without implementing logic.")
    return ptw.read(io_file)


def deserialize_persistent(
        object_id, 
        class_id, 
        objects_map  # final Map<ObjectID, Reference<DataClayObject>>
):

    obj = None
    try:
        obj = objects_map[object_id]
        logger.debug("Hit of ObjectID: {%s} on the object map", object_id)
    except KeyError:
        logger.debug("Miss for ObjectID: {%s}, not present in objects map",
                         object_id)
        try:
            obj = runtime.inmemory_objects[object_id]
        except KeyError:
            obj = runtime.new_instance(class_id,
                                        persistent_flag=True,
                                        loaded_flag=False,
                                        proxy_flag=False,
                                        object_id=object_id)
            runtime.inmemory_objects[object_id] = obj
        objects_map[object_id] = obj
    return obj
