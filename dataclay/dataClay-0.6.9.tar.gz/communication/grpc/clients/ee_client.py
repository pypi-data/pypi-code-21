"""gRPC ExecutionEnvironment Client code - StorageLocation methods."""

from communication.grpc import utils
from communication.grpc.generated.dataservice import dataservice_pb2, dataservice_pb2_grpc
from communication.grpc.messages.dataservice import dataservice_messages_pb2, dataservice_messages_pb2_grpc
import dataclay.core
from dataclay.core.exceptions.__init__ import DataclayException
import grpc
from grpc._cython import cygrpc
import grpc_tools
import logging
import sys
import traceback
import yaml


__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


class EEClient(object):
    channel = None
    ds_stub = None
    
    def __init__(self, hostname, port):
        """Create the stub and the channel at the address passed by the server."""
        # TODO: Add support for multiple channels and stubs
        address = str(hostname) + ":" + str(port)
        options = [(cygrpc.ChannelArgKey.max_send_message_length, 1000 * 1024 * 1024),
                   (cygrpc.ChannelArgKey.max_receive_message_length, 1000 * 1024 * 1024)]
        self.channel = grpc.insecure_channel(address, options)
        self.ds_stub = dataservice_pb2_grpc.DataServiceStub(self.channel)

    def close(self):
        """Closing channel by deleting channel and stub"""
        del self.channel
        del self.ds_stub
        self.channel = None
        self.ds_stub = None

    def ds_deploy_metaclasses(self, namespace_name, deployment_pack):
        deployment_pack_dict = dict()

        for k, v in deployment_pack.iteritems():
            deployment_pack_dict[k] = yaml.dump(v)

        request = dataservice_messages_pb2.DeployMetaClassesRequest(
            namespace=namespace_name,
            deploymentPack=deployment_pack_dict
        )

        try:
            response = self.ds_stub.deployMetaClasses(request)

        except RuntimeError:
            raise

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def ds_new_persistent_instance(self, session_id, class_id, implementation_id, i_face_bitmaps, params):

        logger.debug("Ready to call to a DS to build a new persistent instance for class {%s}",
                     class_id)
        temp_iface_b = dict()
        temp_param = None

        if i_face_bitmaps is not None:
            for k, v in i_face_bitmaps.iteritems():
                temp_iface_b[k] = v

        if params is not None:
            temp_param = utils.get_param_or_return(params)

        request = dataservice_messages_pb2.NewPersistentInstanceRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            classID=utils.get_msg_options['meta_class'](class_id),
            implementationID=utils.get_msg_options['implem'](implementation_id),
            ifaceBitMaps=temp_iface_b,
            params=temp_param
        )

        try:
            response = self.ds_stub.newPersistentInstance(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return utils.get_id(response.objectID)

    def ds_store_objects(self, session_id, objects, moving, ids_with_alias):

        obj_list = []
        id_with_alias_list = []

        for obj in objects:
            obj_list.append(utils.get_obj_with_data_param_or_return(obj))

        if ids_with_alias is not None:
            for id_with_alias in ids_with_alias:
                if id_with_alias is not None:
                    id_with_alias_list.append(utils.get_msg_options['object'](id_with_alias))

        request = dataservice_messages_pb2.StoreObjectsRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objects=obj_list,
            moving=moving,
            idsWithAlias=id_with_alias_list
        )

        try:
            response = self.ds_stub.storeObjects(request)

        except RuntimeError:
            traceback.print_exc(file=sys.stdout)
            raise

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def ds_new_metadata(self, md_infos):

        md_infos_dict = dict()

        for k, v in md_infos.iteritems():

            md_infos_dict[k] = yaml.dump(v)

        request = dataservice_messages_pb2.NewMetaDataRequest(
            mdInfos=md_infos_dict
        )

        try:
            response = self.ds_stub.newMetaData(request)

        except RuntimeError:
            raise

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def ds_get_objects(self, session_id, object_ids, recursive, moving):

        object_ids_list = []
        for oid in object_ids:
            object_ids_list.append(utils.get_msg_options['object'](oid))

        request = dataservice_messages_pb2.GetObjectsRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objectIDS=object_ids_list,
            recursive=recursive,
            moving=moving
        )

        try:
            response = self.ds_stub.getObjects(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)
        
        serialized_objs = list() 
        for obj_with_data in response.objects:
            serialized_objs.append(utils.get_obj_with_data_param_or_return(obj_with_data))
        
        return serialized_objs
    
    def ds_new_version(self, session_id, object_id, metadata_info):

        request = dataservice_messages_pb2.NewVersionRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objectID=utils.get_msg_options['object'](object_id),
            metadataInfo=yaml.dump(metadata_info)
        )

        try:
            response = self.ds_stub.newVersion(request)

        except RuntimeError:
            traceback.print_exc(file=sys.stdout)
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()
        oid = utils.get_id(response.objectID)

        for k, v in response.versionedIDs:
            result[utils.get_id_from_uuid(k)] = utils.get_id_from_uuid(v)

        t = (oid, result)

        return t

    def ds_consolidate_version(self, session_id, version_info):

        request = dataservice_messages_pb2.ConsolidateVersionRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            versionInfo=yaml.dump(version_info)
        )

        try:
            response = self.ds_stub.consolidateVersion(request)

        except RuntimeError:
            raise

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def ds_upsert_objects(self, session_id, object_bytes):

        request = dataservice_messages_pb2.UpsertObjectsRequest

        obj_byt_list = []
        for entry in object_bytes:
            obj_byt_list.append(utils.get_obj_with_data_param_or_return(entry))

        try:
            response = self.ds_stub.upsertObjects(request(
                sessionID=utils.get_msg_options['session'](session_id)),
                bytesUpdate=obj_byt_list)

        except RuntimeError:
            raise

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def ds_execute_implementation(self, object_id, implementation_id, session_id, params):

        request = dataservice_messages_pb2.ExecuteImplementationRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            implementationID=utils.get_msg_options['implem'](implementation_id),
            params=utils.get_param_or_return(params),
            objectID=utils.get_msg_options['object'](object_id)
        )

        try:
            response = self.ds_stub.executeImplementation(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        if response.ret is not None:
            return utils.get_param_or_return(response.ret)
        else:
            return None
        
    def ds_new_replica(self, session_id, object_id):

        request = dataservice_messages_pb2.NewReplicaRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objectID=utils.get_msg_options['object'](object_id)
        )

        try:
            response = self.ds_stub.newReplica(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = set()

        for oid in response.replicatedIDs:
            result.add(utils.get_id(oid))

        return result

    def ds_move_objects(self, session_id, object_id, dest_st_location, recursive):

        request = dataservice_messages_pb2.MoveObjectsRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objectID=utils.get_msg_options['object'](object_id),
            destLocID=utils.get_msg_options['storage_loc'](dest_st_location),
            recursive=recursive
        )

        try:
            response = self.ds_stub.moveObjects(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = set()

        for oid in response.movedObjects:
            result.add(utils.get_id(oid))

        return result

    def ds_remove_objects(self, session_id, object_ids, recursive, moving, new_hint):

        obj_ids_list = []
        for oid in object_ids:
            obj_ids_list.append(utils.get_msg_options['object'](oid))

        request = dataservice_messages_pb2.RemoveObjectsRequest(
            sessionID=utils.get_msg_options['session'](session_id),
            objectIDs=obj_ids_list,
            recursive=recursive,
            moving=moving,
            newHint=utils.get_msg_options['exec_env'](new_hint)
        )

        try:
            response = self.ds_stub.removeObjects(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.removedObjects.iteritems():
            result[utils.get_id_from_uuid(k)] = utils.get_id_from_uuid(v)

        return result

    def ds_migrate_objects_to_backends(self, back_ends):

        back_ends_dict = dict()

        for k, v in back_ends.iteritems():
            back_ends_dict[k] = yaml.dump(v)

        request = dataservice_messages_pb2.MigrateObjectsRequest(
            destStorageLocs=back_ends_dict
        )

        try:
            response = self.ds_stub.migrateObjectsToBackends(request)

        except RuntimeError:
            raise

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.migratedObjs.iteritems():
            m_objs = v
            oids = set()

            for oid in m_objs.getObjsList():
                oids.add(utils.get_id(oid))

            result[utils.get_id_from_uuid(k)] = oids

        non_migrated = set()

        for oid in response.nonMigratedObjs.getObjsList():
            non_migrated.add(utils.get_id(oid))

        t = (result, non_migrated)

        return t
