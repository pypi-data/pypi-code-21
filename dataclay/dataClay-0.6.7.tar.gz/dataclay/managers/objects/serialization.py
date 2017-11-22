"""Serialization code related to DataClay objects

The code implemented in this module is (at "this moment") identical to the ones
implemented in the Java package client.CommonLib. Specifically, the serialize*
functions are more or less adapted here.
"""
import logging
import uuid
from io import BytesIO

from dataclay.core.containers import DataClayObjectMetaData
from dataclay.core.exceptions import InvalidPythonSignature
from dataclay.core.primitives import *

from . import IdentityDict

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


def serialize_association(
        io_output,  # final DataClayByteBuffer
        element,  # final DataClayObject
        cur_serialized_objs,  # final IdentityHashMap<Object, Integer>
        pending_objs  # ListIterator<DataClayObject>
):
    try:
        tag = cur_serialized_objs[element]
    except KeyError:
        #pending_objs.append(element)
        tag = len(cur_serialized_objs)
        cur_serialized_objs[element] = tag

    Vlq().write(io_output, tag)


def serialize_params_or_return(
        params,  # final Object[]
        iface_bitmaps,  # final Map<MetaClassID, byte[]>
        params_spec,  # final Map<String, Type>
        params_order,  # final List<String>
):
    pending_objects = list()
    already_serialized_params = set()
    
    imm_objs = dict()
    lang_objs = dict()
    vol_params = dict()
    pers_params = dict()

    i = 0
    num_params = len(params_order)
    if num_params > 0:
        for param_name in params_order:
    
            param = params[i]
            if param is not None:

                real_type = type(param)
                logger.debug("Ready to serialize following param: %r (type: %s)",
                             param, real_type)

                if real_type.__name__ == "Future" and \
                                real_type.__module__ == "pycompss.runtime.binding":
                    from pycompss.api.api import compss_wait_on
                    logger.info("Received a `Future` PyCOMPSs object, waiting for the real object...")
                    param = compss_wait_on(param)
                    real_type = type(param)
                    logger.info("Using the parameter: %r (type: %s)",
                                param, real_type)

                # ToDo: support for notifications (which is said to leave params_spec None)
                param_type = params_spec[param_name]
    
              
                try:
                    oid = param._dclay_instance_extradata.object_id
                    
                    if param.is_persistent():
                        class_id = param._dclay_class_extradata.class_id
                        pers_param = [oid, None, class_id, False]
                        pers_params[i] = pers_param
                        
                    else:
                        # this is no-exception flow which means...
                        # ... means that it is a volatile object to serialize, with its OID            
                        already_serialized_params.add(oid)
                        obj_with_data = serialize_dcobj_with_data(
                                    param,  # final DataClayObject
                                    pending_objects,  # final ListIterator<DataClayObject>
                                    False,
                                    None)
                        vol_params[i] = obj_with_data 
    
                except AttributeError:
                    try:
                        ptw = PyTypeWildcard(param_type.signature)
                    except InvalidPythonSignature:
                        raise NotImplementedError("In fact, InvalidPythonSignature was "
                                                  "not even implemented, seems somebody is "
                                                  "raising it without implementing logic.")
                    else:
                        io_output = BytesIO()
                        ptw.write(io_output, param)
                        imm_objs[i] = io_output
            i = i + 1
    
        while pending_objects:
            # Note that pending objects are *only* DataClay Objects)
            pending_obj = pending_objects.pop()
            oid = pending_obj._dclay_instance_extradata.object_id
    
            if oid in already_serialized_params:
                continue
             
            if pending_obj.is_persistent:
                    class_id = param._dclay_class_extradata.class_id
                    pers_param = [oid, None, class_id, False]
                    pers_params[i] = pers_param
            else:
                obj_with_data = serialize_dcobj_with_data(
                                        pending_obj,  # final DataClayObject
                                        pending_objects,  # final ListIterator<DataClayObject>
                                        False,
                                        None,
                                        None)
            
                vol_params[i] = obj_with_data 
    
            # Ensure that it is put inside
            already_serialized_params.add(oid)
            i += 1
    else:
        logger.debug("Call with no parameters, no serialization required")

    serialized_params = [num_params, imm_objs, lang_objs, vol_params, pers_params]

    return serialized_params


def serialize_metadata(
        io_output,  # final DataClayByteBuffer
        cur_ser_objs,  # final IdentityHashMap<Object, Integer>
        map_oids_tags_to_oid_and_class_tags,  # final Map<Integer, Triple<ObjectID, DataSetID, Integer>>
        map_class_tags_to_class_ids,  # final Map<Integer, MetaClassID>
        map_proxies,  # final Map<Integer, Boolean>
        is_for_store,  # final boolean
        store_dataset  # final DataSetID
):
    # Revert the dictionary
    map_class_ids_to_class_tags = {v: k for k, v in map_class_tags_to_class_ids.iteritems()}

    # The IdentityDict behaves well for this kind of iteration
    for dc_object, oid_tag in cur_ser_objs:
        class_extradata = dc_object._dclay_class_extradata
        instance_extradata = dc_object._dclay_instance_extradata

        class_id = class_extradata.class_id
        assert class_id is not None

        object_id = instance_extradata.object_id
        # Ensure the object has a valid ObjectID
        if not object_id:
            object_id = uuid.uuid4()
            instance_extradata.object_id = object_id

        dataset_id = instance_extradata.dataset_id
        if dataset_id is None and is_for_store:
            dataset_id = store_dataset
            instance_extradata.dataset_id = dataset_id
            # otherwise -> volatile, DataSetID is null

        # Get class tag and ensure consistency in maps
        try:
            class_tag = map_class_ids_to_class_tags[class_id]
        except KeyError:
            class_tag = len(map_class_ids_to_class_tags)
            map_class_ids_to_class_tags[class_id] = class_tag

        if class_tag not in map_class_tags_to_class_ids:
            map_class_tags_to_class_ids[class_tag] = class_id

        map_oids_tags_to_oid_and_class_tags[oid_tag] = (object_id, dataset_id, class_tag)
        map_proxies[oid_tag] = instance_extradata.proxy_flag or False  # None is not a good value

    DataClayObjectMetaData(map_oids_tags_to_oid_and_class_tags,
                           map_class_tags_to_class_ids,
                           map_proxies).serialize(io_output)


def serialize_dcobj_with_data(
        dc_object,  # final DataClayObject
        #  dc_buffer,  # final DataClayByteBuffer <-- change
        pending_objs,  # final ListIterator<DataClayObject>
        ignore_user_types,  # final boolean
        hint

):
    dco_extradata = dc_object._dclay_instance_extradata
    dcc_extradata = dc_object._dclay_class_extradata
    io_body = BytesIO()
    dco_id = dco_extradata.object_id

    # Ensure the dc_object has an object_id
    if not dco_id:
        dco_id = uuid.uuid4()
        dco_extradata.object_id = dco_id

    # Those behave almost identical to Java's IdentityHashMap
    cur_ser_objs = IdentityDict()
    cur_ser_objs[dc_object] = 0
    cur_ser_python_objs = IdentityDict()

    # FIXME complain for Proxy instances
    # We start by the body because we need some extras
    dc_object.serialize(io_body, ignore_user_types, None,
                        cur_ser_objs, pending_objs, cur_ser_python_objs)

    # Structures for the MetaData:
    map_oids = {0: dco_id}
    map_class_tags_to_class_ids = {0: dcc_extradata.class_id}
    map_hints = {}
    if hint is not None:
        map_hints = {0: hint}
    list_proxies = [dco_extradata.proxy_flag]
    num_refs = 0

    metadata = map_oids, map_class_tags_to_class_ids, map_hints, list_proxies, num_refs

    return dco_extradata.object_id, dcc_extradata.class_id, metadata, io_body
