"""gRPC ExecutionEnvironment Server code - StorageLocation/EE methods."""

from communication.grpc import utils
from communication.grpc.generated.dataservice import dataservice_pb2_grpc as ds
from communication.grpc.messages.common import common_messages_pb2
from communication.grpc.messages.dataservice import dataservice_messages_pb2
from dataclay import runtime
from dataclay.core.exceptions.__init__ import DataclayException
from dclay_server import operations
from io import BytesIO
import logging
import sys
import traceback
import yaml


__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class DataServiceEE(ds.DataServiceServicer):

    client = None

    def ass_client(self):
        self.client = runtime.ready_clients["@STORAGE"]

    def deployMetaClasses(self, request, context):

        try:
            namespace = request.namespace
            classes_map_yamls = request.deploymentPack 
            operations.ds_deploy_metaclasses(namespace, classes_map_yamls)
            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[deployMetaClasses] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'namespace name' and 'deployment pack'",
                                                             utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[deployMetaClasses] Received NotImplementedError with message:\n%s", e.message)

            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=utils.prepare_exception("Check parameters: 'namespace name' and 'deployment pack'",
                                                         utils.return_stack())
            )

    def newPersistentInstance(self, request, context):

        try:
            iface_bit_maps = {}

            for k, v in request.ifaceBitMaps.iteritems():
                iface_bit_maps[utils.get_id_from_uuid(k)] = bytes(v)

            params = []

            if request.params:
                params = utils.get_param_or_return(request.params)

            oid = self.client.ds_new_persistent_instance(utils.get_id(request.sessionID),
                                                         utils.get_id(request.classID),
                                                         utils.get_id(request.implementationID),
                                                         iface_bit_maps,
                                                         params)

            return dataservice_messages_pb2.NewPersistentInstanceResponse(objectID=utils.get_msg_options['object'](oid))

        except DataclayException as e:
            logger.warning("[newPersistentInstance] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewPersistentInstanceResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'class_id',"
                                                             " 'implementation_id', 'i_face_bitmaps' and 'params'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newPersistentInstance] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewPersistentInstanceResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'class_id',"
                                                             " 'implementation_id', 'i_face_bitmaps' and 'params'",
                                                             utils.return_stack()))
            )

    def storeObjects(self, request, context):

        
    
        try:
            objects_list = []
            for vol_param in request.objects:
                param = utils.get_obj_with_data_param_or_return(vol_param)
                serialized_obj = BytesIO(param[3])
                dcobj = param[0], param[1], param[2], serialized_obj
                objects_list.append(dcobj)

            ids_with_alias_set = set()
            if request.idsWithAlias is not None and len(request.idsWithAlias) > 0:
                for ids_with_alias in request.idsWithAlias:
                    ids_with_alias_set.add(utils.get_id(ids_with_alias))

            self.client.ds_store_objects(utils.get_id(request.sessionID),
                                         objects_list, request.moving, ids_with_alias_set)

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[storeObjects] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'objects', 'moving'"
                                                             " and 'ids_with_alias'",
                                                             utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[storeObjects] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'objects', 'moving'"
                                                         " and 'ids_with_alias'",
                                                         utils.return_stack())
            )
        
    def executeImplementation(self, request, context):

        try:
            object_id = utils.get_id(request.objectID)
            implementation_id = utils.get_id(request.implementationID)
            serialized_params = utils.get_param_or_return(request.params)
            session_id = utils.get_id(request.sessionID)
            try:
                result = operations.ds_exec_impl(object_id, implementation_id, serialized_params, session_id)
            except DataclayException as de:
                logger.info("ExecuteImplementation finished with exception %s" % str(de))
                return dataservice_messages_pb2.ExecuteImplementationResponse(
                    excInfo=common_messages_pb2.ExceptionInfo(
                        isException=True,
                        exceptionMessage=utils.prepare_exception("Exception Message", utils.return_stack()))
                )
            logger.info("ExecuteImplementation finished, sending response")

            return dataservice_messages_pb2.ExecuteImplementationResponse(ret=utils.get_param_or_return(result))

        # ToDo: Understand how to serialize and send exception

        except DataclayException as e:
            logger.warning("[executeImplementation] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.ExecuteImplementationResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    serializedException=bytes(e),
                    exceptionMessage=utils.prepare_exception("Check parameters: 'object_id', 'implementation_id',"
                                                             " 'session_id' and 'params'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[executeImplementation] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.ExecuteImplementationResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'object_id', 'implementation_id',"
                                                             " 'session_id' and 'params'",
                                                             utils.return_stack()))
            )

    def getObjects(self, request, context):

        try:
            object_ids = set()
            for oid in request.objectIDS:
                object_ids.add(utils.get_id(oid))

            result = self.client.ds_get_objects(utils.get_id(request.sessionID),
                                                object_ids,
                                                request.recursive)

            obj_list = []

            for entry in result:
                obj_list.append(utils.get_obj_with_data_param_or_return(entry))

            return dataservice_messages_pb2.GetObjectsResponse(objects=obj_list)

        except DataclayException as e:
            logger.warning("[getObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.GetObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive' and 'moving'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[getObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.GetObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive' and 'moving'",
                                                             utils.return_stack()))
            )

    def newMetaData(self, request, context):

        try:
            md_infos = {}

            for k, v in request.mdInfos.iteritems():

                md_infos[utils.get_id_from_uuid(k)] = yaml.load(v)

            self.client.ds_new_metadata(md_infos)

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[newMetaData] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameter: 'md_infos'",
                                                             utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[newMetaData] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=utils.prepare_exception("Check parameter: 'md_infos'",
                                                         utils.return_stack())
            )

    def newVersion(self, request, context):

        try:
            result = self.client.ds_new_version(
                utils.get_id(request.sessionID),
                utils.get_id(request.objectID),
                yaml.load(request.metadataInfo)
            )

            vers_ids = dict()

            # ToDo: check it
            for k, v in result[1].iteritems():
                vers_ids[k] = v

            return dataservice_messages_pb2.NewVersionResponse(
                objectID=utils.get_msg_options['object'](result[0]),
                versionedIDs=vers_ids
            )

        except DataclayException as e:
            logger.warning("[newVersion] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewVersionResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_id'"
                                                             " and 'metadata_info'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newVersion] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewVersionResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_id'"
                                                             " and 'metadata_info'",
                                                             utils.return_stack()))
            )

    def consolidateVersion(self, request, context):

        try:
            self.client.ds_consolidate_version(utils.get_id(request.sessionID),
                                               yaml.load(request.versionInfo))

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[consolidateVersion] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'version_info'",
                                                             utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[consolidateVersion] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'version_info'",
                                                         utils.return_stack())
            )

    def upsertObjects(self, request, context):

        try:
            session_id = utils.get_id(request.sessionID)

            objects = []
            for entry in request.bytesUpdate:
                objects.append(utils.get_obj_with_data_param_or_return(entry))

            self.client.ds_upsert_objects(session_id, objects)

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[upsertObjects] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'object_bytes'",
                                                             utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[upsertObjects] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'object_bytes'",
                                                         utils.return_stack())
            )

    def newReplica(self, request, context):

        ##### NOT WELL IMPL. NEW ALGORITHM MISSING FOR MOVING OBJECTS CHECKING FIRST THE MEMORY ######

        try:
            result = self.client.ds_new_replica(utils.get_id(request.sessionID),
                                                utils.get_id(request.objectID))

            repl_ids_list = []

            for oid in result:
                repl_ids_list.append(utils.get_msg_options['object'](oid))

            return dataservice_messages_pb2.NewReplicaResponse(
                replicatedIDs=repl_ids_list
            )

        except DataclayException as e:
            logger.warning("[newReplica] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewReplicaResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'object_id'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newReplica] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewReplicaResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id' and 'object_id'",
                                                             utils.return_stack()))
            )

    def moveObjects(self, request, context):

        ##### NOT WELL IMPL. NEW ALGORITHM MISSING FOR MOVING OBJECTS CHECKING FIRST THE MEMORY ######

        try:
            result = self.client.ds_move_objects(utils.get_id(request.sessionID),
                                                 utils.get_id(request.objectID),
                                                 utils.get_id(request.destLocID),
                                                 request.recursive)

            mov_obj_list = []

            for oid in result:
                mov_obj_list.append(utils.get_msg_options['object'](oid))

            return dataservice_messages_pb2.MoveObjectsResponse(
                movedObjects=mov_obj_list
            )

        except DataclayException as e:
            logger.warning("[moveObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.MoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_id',"
                                                             " 'dest_st_location' and 'recursive'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[moveObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.MoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_id',"
                                                             " 'dest_st_location' and 'recursive'",
                                                             utils.return_stack()))
            )

    def removeObjects(self, request, context):

        try:
            object_ids = set()

            for oid in request.getObjectsIDSList():
                object_ids.add(utils.get_id(oid))

            result = self.client.ds_remove_objects(utils.get_id(request.sessionID),
                                                   object_ids,
                                                   request.recursive,
                                                   request.moving,
                                                   utils.get_id(request.newHint))

            rem_obj = dict()

            for k, v in result.iteritems():
                rem_obj[str(k)] = str(v)

            return dataservice_messages_pb2.RemoveObjectsResponse(
                removedObjects=rem_obj
            )

        except DataclayException as e:
            logger.warning("[removeObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.RemoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive', 'moving' and 'new_hint'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[removeObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.RemoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive', 'moving' and 'new_hint'",
                                                             utils.return_stack()))
            )

    def migrateObjectsToBackends(self, request, context):

        try:
            backends = dict()

            for k, v in request.destStorageLocs.iteritems():
                backends[utils.get_id_from_uuid(k)] = yaml.load(v)

            result = self.client.ds_migrate_objects_to_backends(backends)

            migr_obj_res = dict()

            for k, v in result[0].iteritems():
                migrated_obj_builder = dataservice_messages_pb2.MigratedObjects()

                for oid in v:
                    migrated_obj_builder(objs=utils.get_msg_options['object'](oid))
                migr_obj_res[str(k)] = migrated_obj_builder

            non_migrated_objs_builder = dataservice_messages_pb2.MigratedObjects()

            non_migr_obj_res = []

            for oid in result[1]:
                non_migrated_objs_builder(objs=utils.get_msg_options['object'](oid))

            non_migr_obj_res.append(non_migrated_objs_builder)

            return dataservice_messages_pb2.MigrateObjectsResponse(
                migratedObjs=migr_obj_res,
                nonMigratedObjs=non_migr_obj_res
            )

        except DataclayException as e:
            logger.warning("[migrateObjectsToBackends] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.MigrateObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameter: 'back_ends'",
                                                             utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[migrateObjectsToBackends] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.MigrateObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=utils.prepare_exception("Check parameter: 'back_ends'",
                                                             utils.return_stack()))
            )
