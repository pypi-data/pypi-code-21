import abc
from typing import Dict, Any

import asyncio
from bson import ObjectId, Timestamp
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import CursorType

from mongo_observer.conf import logger
from mongo_observer.models import Operations, Document


class OperationHandler(metaclass=abc.ABCMeta):
    def __init__(self):
        self.handlers = {
            Operations.INSERT: self.on_insert,
            Operations.UPDATE: self.on_update,
            Operations.DELETE: self.on_delete
        }
        self.last_timestamp: Timestamp = None

    async def handle(self, operation: Dict[str, Any]):
        try:
            self.last_timestamp = operation['ts']
            handler = self.handlers[operation['op']]
        except KeyError:
            logger.debug({'info': 'skipping operation', 'operation': operation})
        else:
            await handler(operation)

    @abc.abstractmethod
    async def on_insert(self, operation: Dict[str, Any]):
        """
        :param operation: A dict containing a document corresponding
        to an operation on oplog. It will contain the following keys:

            * `ts`: Timestamp of the operationa
            * `h`: An unique signed long identifier of the operation
            * `op`: A character representing the type of the operation
            * `ns`: A namespace string formed with the concatenation
            of 'database.collection'
            * `o`: The inserted document
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def on_update(self, operation: Dict[str, Any]):
        """
        :param operation: A dict containing a document corresponding
        to an operation on oplog. It will contain the following keys:

            * `ts`: Timestamp of the operation
            * `h`: An unique signed long identifier of the operation
            * `op`: A character representing the type of the operation
            * `ns`: A namespace string formed with the concatenation
            of 'database.collection'
            * `o`: A dict with a single _id key of the document to be updated
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def on_delete(self, operation: Dict[str, Any]):
        """
        :param operation: A dict containing a document corresponding
        to an operation on oplog. It will contain the following keys:

            * `ts`: Timestamp of the operation
            * `h`: An unique signed long identifier of the operation
            * `op`: A character representing the type of the operation
            * `ns`: A namespace string formed with the concatenation
            of 'database.collection'
            * `o`: The operation data performed on the document
            * `o2`: A dict with a single _id key, of the deleted document
        """
        raise NotImplementedError()


class ReactiveCollection(OperationHandler):
    def __init__(self,
                 collection: Dict[ObjectId, Dict],
                 remote_collection: AsyncIOMotorCollection):
        super().__init__()
        self.collection = collection
        self.remote_collection = remote_collection

    @classmethod
    async def init_async(cls, remote_collection: AsyncIOMotorCollection):
        cursor = remote_collection.find({})
        collection = {doc['_id']: Document(doc) async for doc in cursor}
        return cls(collection, remote_collection)

    async def on_update(self, operation: Dict[str, Any]):
        doc = self.collection[operation['o2']['_id']]
        change = operation['o']
        if '$set' in change:
            doc.update(change['$set'])
        if '$unset' in change:
            for key, _ in change['$unset'].items():
                doc.pop(key, None)
        return doc

    async def on_insert(self, operation: Dict[str, Any]):
        doc = operation['o']
        self.collection[doc['_id']] = Document(doc)
        return doc

    async def on_delete(self, operation: Dict[str, Any]):
        doc = operation['o']
        del self.collection[doc['_id']]


class ReactivePartialCollection(ReactiveCollection):
    sleep_time = 1

    def __init__(self,
                 collection: Dict[ObjectId, Dict],
                 remote_collection: AsyncIOMotorCollection,
                 filter: Dict):
        super().__init__(collection, remote_collection)
        self.filter = filter
        self._last_inserted_document = None

    @classmethod
    async def init_async(cls, remote_collection: AsyncIOMotorCollection,
                         *args, **kwargs):
        filter = kwargs.pop('filter', {})
        return cls({}, remote_collection, filter)

    async def on_insert(self, operation: Dict[str, Any]):
        pass

    async def on_delete(self, operation: Dict[str, Any]):
        try:
            super(ReactivePartialCollection, self).on_delete(operation)
        except KeyError:
            pass

    def get_new_cursor(self):
        filter = self.filter.copy()
        if self._last_inserted_document:
            filter['_id'] = {"$gt": self._last_inserted_document['_id']}

        return self.remote_collection.find(filter)

    def handle_new_doc(self, doc):
        self.collection[doc['_id']] = Document(doc)
        self._last_inserted_document = doc

    async def observe_changes(self):
        cursor = self.get_new_cursor()
        while True:
            if not cursor.alive:
                await asyncio.sleep(self.sleep_time)
                cursor = self.get_new_cursor()

            empty_cursor = True
            async for doc in cursor:
                empty_cursor = False
                self.handle_new_doc(doc)
            if empty_cursor:
                print("Cursor is empty")
