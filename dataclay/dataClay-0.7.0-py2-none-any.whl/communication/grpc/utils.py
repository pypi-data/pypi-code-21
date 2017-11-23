"""Utility methods for gRPC clients/server."""

from dataclay.core.constants import lang_codes
import logging
import sys
import traceback
import uuid

import communication.grpc.messages.common.common_messages_pb2 as common_messages


__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


def get_credential(cred):
    """Get the pwdCredential of the corresponding protobuf message.

    :param cred: PasswordCredential/Credential protobuf message.
    :return: Depends on the param can return a Credential protobuf message or a PasswordCredential.
    """
    if cred is common_messages.Credential:
        if cred is None:
            return None
        else:
            return cred.password
    else:
        if cred is None:
            return common_messages.Credential()
        else:
            return common_messages.Credential(password=cred[1])


"""get_msg_id_x.

:param x_id: UUID.
:return: ID protobuf message.
"""


def get_msg_id_account(account_id):
    if account_id is None:

        return common_messages.AccountID()
    else:
        return common_messages.AccountID(
            uuid=str(account_id))


def get_msg_id_contract(contract_id):
    if contract_id is None:

        return common_messages.ContractID()
    else:
        return common_messages.ContractID(
            uuid=str(contract_id))


def get_msg_id_credential(credential_id):
    if credential_id is None:

        return common_messages.CredentialID()
    else:

        return common_messages.CredentialID(
            uuid=str(credential_id))


def get_msg_id_datacontract(dc_id):
    if dc_id is None:

        return common_messages.DataContractID()
    else:
        return common_messages.DataContractID(
            uuid=str(dc_id))


def get_msg_id_dataset(dataset_id):
    if dataset_id is None:

        return common_messages.DataSetID()
    else:
        return common_messages.DataSetID(
            uuid=str(dataset_id))


def get_msg_id_namespace(namespace_id):
    if namespace_id is None:

        return common_messages.NamespaceID()
    else:
        return common_messages.NamespaceID(
            uuid=str(namespace_id))


def get_msg_id_class(class_id):
    if class_id is None:

        return common_messages.MetaClassID()
    else:
        return common_messages.MetaClassID(
            uuid=str(class_id))


def get_msg_id_eca(eca_id):
    if eca_id is None:

        return common_messages.ECAID()
    else:
        return common_messages.ECAID(
            uuid=str(eca_id))


def get_msg_id_event_message(event_message_id):
    if event_message_id is None:

        return common_messages.EventMessageID()
    else:
        return common_messages.EventMessageID(
            uuid=str(event_message_id))


def get_msg_id_event_obj_meet_cond(event_omc_id):
    if event_omc_id is None:

        return common_messages.EventObjsMeetConditionID()
    else:
        return common_messages.EventObjsMeetConditionID(
            uuid=str(event_omc_id))


def get_msg_id_exec_env(ee_id):
    if ee_id is None:

        return common_messages.ExecutionEnvironmentID()
    else:
        return common_messages.ExecutionEnvironmentID(
            uuid=str(ee_id))


def get_msg_id_implem(implem_id):
    if implem_id is None:

        return common_messages.ImplementationID()
    else:
        return common_messages.ImplementationID(
            uuid=str(implem_id))


def get_msg_id_interface(interface_id):
    if interface_id is None:

        return common_messages.InterfaceID()
    else:
        return common_messages.InterfaceID(
            uuid=str(interface_id))


def get_msg_id_meta_class(meta_class_id):
    if meta_class_id is None:

        return common_messages.MetaClassID()
    else:
        return common_messages.MetaClassID(
            uuid=str(meta_class_id))


def get_msg_id_object(object_id):
    if object_id is None:

        return common_messages.ObjectID()
    else:
        return common_messages.ObjectID(
            uuid=str(object_id))


def get_msg_id_operation(operation_id):
    if operation_id is None:

        return common_messages.OperationID()
    else:
        return common_messages.OperationID(
            uuid=str(operation_id))


def get_msg_id_property(property_id):
    if property_id is None:

        return common_messages.PropertyID()
    else:
        return common_messages.PropertyID(
            uuid=str(property_id))


def get_msg_id_qual_reg(qual_reg_id):
    if qual_reg_id is None:

        return common_messages.QualitativeRegistryID()
    else:
        return common_messages.QualitativeRegistryID(
            uuid=str(qual_reg_id))


def get_msg_id_resource(resource_id):
    if resource_id is None:

        return common_messages.ResourceID()
    else:
        return common_messages.ResourceID(
            uuid=str(resource_id))


def get_msg_id_session(session_id):
    if session_id is None:

        return common_messages.SessionID()
    else:
        return common_messages.SessionID(
            uuid=str(session_id))


def get_msg_id_storage_loc(storage_loc_id):
    if storage_loc_id is None:

        return common_messages.StorageLocationID()
    else:
        return common_messages.StorageLocationID(
            uuid=str(storage_loc_id))
        
def get_msg_id_backend_id(backend_id):
    if backend_id is None:

        return common_messages.ExecutionEnvironmentID()
    else:
        return common_messages.ExecutionEnvironmentID(
            uuid=str(backend_id))


get_msg_options = {'account': get_msg_id_account,
                   'contract': get_msg_id_contract,
                   'credential': get_msg_id_credential,
                   'datacontract': get_msg_id_datacontract,
                   'dataset': get_msg_id_dataset,
                   'namespace': get_msg_id_namespace,
                   'eca': get_msg_id_eca,
                   'event_message': get_msg_id_event_message,
                   'obj_meet_cond': get_msg_id_event_obj_meet_cond,
                   'exec_env': get_msg_id_exec_env,
                   'implem': get_msg_id_implem,
                   'interface': get_msg_id_interface,
                   'meta_class': get_msg_id_meta_class,
                   'object': get_msg_id_object,
                   'operation': get_msg_id_operation,
                   'property': get_msg_id_property,
                   'qual_reg': get_msg_id_qual_reg,
                   'resource': get_msg_id_resource,
                   'session': get_msg_id_session,
                   'storage_loc': get_msg_id_storage_loc,
                   'backend_id': get_msg_id_backend_id,
                   'class': get_msg_id_class}


def get_id(id_msg):
    """Create the ID based on protobuf message.

    :param id_msg: Common protobuf message with uuid_most and uuid_least.
    :return: UUID based on param.
    """    
    if id_msg is None:
        return None
    elif id_msg.uuid is None:
        return None
    elif id_msg.uuid == "":
        return None
    else:
        return uuid.UUID(id_msg.uuid)


def get_id_from_uuid(msg_str):
    """Create the ID based on id message.

    :param msg_str: string UUID.
    :return: Correct UUID.
    """
    if msg_str is None or msg_str == "":
        return None
    else:
        return uuid.UUID(msg_str)


def get_language(msg_langs):
    """Get the correct language.

    :param msg_langs: Could be a Langs protobuf message or not.
    :return: The number of languages that are in the protobuf message if is it or
            a default instance of Langs protobuf message.
    """
    if msg_langs is common_messages.Langs:
        return msg_langs.number
    else:
        if msg_langs == lang_codes.LANG_PYTHON:
            return 2
        elif msg_langs == lang_codes.LANG_JAVA:
            return 1
        else:
            return 0


def get_metadata(metadata):
    """Get Metadata GRPC message from DataclayMetaData.

    :param metadata: DataClayMetaData.
    :return: MetaData GRPC message.
    """
    if type(metadata) is common_messages.DataClayObjectMetaData:
       
        oids = dict()
        for k, v in metadata.oids.iteritems():
            oids[k] = get_id(v)
        
        classids = dict()
        for k, v in metadata.classids.iteritems():
            classids[k] = get_id(v)
            
        hints = dict()
        for k, v in metadata.hints.iteritems():
            hints[k] = get_id(v)
            
        proxies = list()
        for p in metadata.proxies:
            proxies.append(p)
        
        num_refs = metadata.numRefs
        
        return oids, classids, hints, proxies, num_refs

    else:

        one = dict()
    
        for k, v in metadata[0].iteritems():
            one[k] = get_msg_options['object'](v)
    
        two = dict()
    
        for k, v in metadata[1].iteritems():
            two[k] = get_msg_options['meta_class'](v)
    
        three = dict()
    
        for k, v in metadata[2].iteritems():
            three[k] = get_msg_options['exec_env'](v)
    
        proxy_tag = []
    
        for pt in metadata[3]:
            proxy_tag.append(pt)
    
        request = common_messages.DataClayObjectMetaData(
            oids=one,
            classids=two,
            hints=three,
            proxies=proxy_tag,
            numRefs=metadata[4]
        )
    
        return request


def to_hex(val, nbits):
    """Convert a long to hex.

    :param val: long 
    :param nbits: The number of bit two's complement.
    :return: hex value.
    """
    return hex((val + (1 << nbits)) % (1 << nbits))


def convert_neg(x):
    """Convert negative hex not correctly converted.

    :param x: int.
    :return: Correct int.
    """
    if x > 9223372036854775808:
        x -= 18446744073709551616
    return x


def get_obj_with_data_param_or_return(vol_param_or_ret):
    """
    
    :param vol_param_or_ret: Could be a protobuf msg or a .
    :return: .
    """
    if type(vol_param_or_ret) is common_messages.ObjectWithDataParamOrReturn:
        oid = get_id(vol_param_or_ret.oid)
        class_id = get_id(vol_param_or_ret.classid)
        mdata = get_metadata(vol_param_or_ret.metadata)
        byte_array = vol_param_or_ret.objbytes
        # logger.info("OID is " + str(vol_param_or_ret.oid))
        # logger.info("Receiving Message bytes are " + bye_to_hex(byte_array)[-50:])
        return oid, class_id, mdata, byte_array
    else:
        # logger.info("OID is " + str(vol_param_or_ret[0]))
        # logger.info("Sending objbytes " + bye_to_hex(vol_param_or_ret[3].getvalue())[-50:])

        response = common_messages.ObjectWithDataParamOrReturn(
            oid=get_msg_options['object'](vol_param_or_ret[0]),
            classid=get_msg_options['meta_class'](vol_param_or_ret[1]),
            metadata=get_metadata(vol_param_or_ret[2]),
            objbytes=vol_param_or_ret[3].getvalue()
        )
        return response


def get_lang_param_or_return(param_or_ret):
    """
    
    :param param_or_ret: Could be a protobuf msg or a .
    :return: .
    """

    if type(param_or_ret) is common_messages.LanguageParamOrReturn:
        mdata = get_metadata(param_or_ret.metadata)
        byte_array = param_or_ret.objbytes
        # logger.info("Receiving Message param lang bytes are " + str(bye_to_hex(byte_array))[-50:])
        return mdata, byte_array

    else:
        # logger.info("Sending lang param bytes " + bye_to_hex(param_or_ret[1].getvalue())[-50:])
        request = common_messages.LanguageParamOrReturn(
            metadata=get_metadata(param_or_ret[0]),
            objbytes=param_or_ret[1].getvalue()
        )

        return request


def get_immutable_param_or_return(param_or_ret):
    """
    
    :param param_or_ret: Could be a protobuf msg or a .
    :return: .
    """

    if type(param_or_ret) is common_messages.ImmutableParamOrReturn:
        byte_array = param_or_ret.objbytes
        # logger.info("Receiving Message param IMM bytes are " + str(bye_to_hex(byte_array))[-50:])
        return byte_array

    else:
        # logger.info("Sending lang imm bytes " + bye_to_hex(param_or_ret.getvalue())[-50:])
        request = common_messages.ImmutableParamOrReturn(
            objbytes=param_or_ret.getvalue()
        )
        return request


def get_persistent_param_or_return(param_or_ret):
    """

    :param param_or_ret: Could be a protobuf msg or a .
    :return: .
    """
    if type(param_or_ret) is common_messages.PersistentParamOrReturn:
        oid = get_id(param_or_ret.oid)
        class_id = get_id(param_or_ret.classID)
        hint = get_id(param_or_ret.hint)
        is_proxy = param_or_ret.isProxy

        return oid, hint, class_id, is_proxy

    else:

        class_id = None
        hint = None
        oid = param_or_ret[0]
        is_proxy = param_or_ret[3]

        if param_or_ret[1] is not None:
            hint = param_or_ret[1]

        if param_or_ret[2] is not None:
            class_id = param_or_ret[2]

        request = common_messages.PersistentParamOrReturn(
            oid=get_msg_options['object'](oid),
            hint=get_msg_options['exec_env'](hint),
            classID=get_msg_options['meta_class'](class_id),
            isProxy=is_proxy)

        return request


def get_param_or_return(param_or_ret_msg):
    """

    :param param_or_ret_msg: Could be None, a protobuf msg or a dict.
    :return: Could return a default SerializedParametersOrReturn, a set of parameters and objects details 
             or a SerializedParametersOrReturn request
    """

    # FIXME: different for serializing and deserializing
    if param_or_ret_msg is None:
        return common_messages.SerializedParametersOrReturn()
    elif type(param_or_ret_msg) is common_messages.SerializedParametersOrReturn:

        num_params = param_or_ret_msg.numParams
    
        imm_objs = dict()       
        lang_objs = dict()
        vol_objs = dict()
        pers_objs = dict()
    
        for k, v in param_or_ret_msg.immParams.iteritems():
            imm_objs[k] = get_immutable_param_or_return(v)
        
        for k, v in param_or_ret_msg.langParams.iteritems():
            lang_objs[k] = get_lang_param_or_return(v)
        
        for k, v in param_or_ret_msg.volatileParams.iteritems():
            vol_objs[k] = get_obj_with_data_param_or_return(v)
        
        for k, v in param_or_ret_msg.persParams.iteritems():
            pers_objs[k] = get_persistent_param_or_return(v)
            
        return num_params, imm_objs, lang_objs, vol_objs, pers_objs
    else:
        num_params = param_or_ret_msg[0]
        imm_objs = dict()
        lang_objs = dict()
        vol_objs = dict()
        pers_obj = dict()
        
        for k, v in param_or_ret_msg[1].iteritems():
            imm_objs[k] = get_immutable_param_or_return(v)
        
        for k, v in param_or_ret_msg[2].iteritems():
            lang_objs[k] = get_lang_param_or_return(v)
        
        for k, v in param_or_ret_msg[3].iteritems():
            vol_objs[k] = get_obj_with_data_param_or_return(v)
        
        for k, v in param_or_ret_msg[4].iteritems():
            pers_obj[k] = get_persistent_param_or_return(v)

        request = common_messages.SerializedParametersOrReturn(
                numParams=num_params,
                immParams=imm_objs,
                langParams=lang_objs,
                volatileParams=vol_objs,
                persParams=pers_obj
        )
    
        return request


def return_empty_message(resp_obs):
    """Return a protobuf empty message.

    :param resp_obs: string msg with UUID.
    """
    resp = common_messages.EmptyMessage()
    resp_obs(resp)


"""
HexByteConversion

Convert a byte string to it's hex representation for output or visa versa.

bye_to_hex converts byte string "\xFF\xFE\x00\x01" to the string "FF FE 00 01"
hex_to_byte converts string "FF FE 00 01" to the byte string "\xFF\xFE\x00\x01"
"""


def bye_to_hex(byte_str):
    """Convert a byte string to it's hex string representation e.g. for output.

    :param byte_str: byte string with UUID.
    :return: hex string msg with UUID.
    """

    print "byte_to_hex", type(byte_str)

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    return ''.join(["%02X " % ord(x) for x in byte_str]).strip()


def hex_to_byte(hex_str):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    :param hex_str: hex string msg with UUID.
    :return: byte string msg with UUID.
    """

    print "byte_to_hex", type(hex_str)

    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )
 
    bytes_str = []

    hex_str = ''.join(hex_str.split(" "))

    for i in range(0, len(hex_str), 2):
        bytes_str.append(chr(int(hex_str[i:i + 2], 16)))

    return ''.join(bytes_str)


def prepare_exception(message, stack):
    """
    Prepare message + stack for proto messages
    :param message: message of the exception.
    :param stack: stackTrace of the exception.
    :return: final string
    """
    return "\n" + "-"*146 + "\nError Message: " + message + "\n" + "-"*146 + "\nServer " + stack + "\n" + "-"*146


def return_stack():
    """
    Create the stack of the obtained exception
    :return: string stacktrace.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)

    return lines[0] + lines[1]
