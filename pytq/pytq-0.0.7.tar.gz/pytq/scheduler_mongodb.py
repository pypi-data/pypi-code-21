#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import collection as collection_module
try:
    from .scheduler import Task, BaseDBTableBackedScheduler, Encoder
except:  # pragma: no cover
    from pytq.scheduler import Task, BaseDBTableBackedScheduler, Encoder


class MongoDBScheduler(BaseDBTableBackedScheduler, Encoder):
    """
    MongoDB collection backed scheduler.

    Feature:

    1. fingerprint of :meth:`~MongoDBScheduler._hash_input()` will be ``_id``
      field in MongoDB collection.
    2. output_data will be serialized and stored in ``out`` field.

    :param collection: :class:`pymongo.Collection`.
    """
    collection = None
    """
    Backend :class:`pymongo.Collection`. You could define that when you
    initiate the scheduler.
    """

    output_key = "_out"
    """
    Default field name used to store output_data
    """

    def __init__(self, logger=None, collection=None):
        super(MongoDBScheduler, self).__init__(logger=logger)
        self.prepare_collection(collection)
        self.link_encode_method()

    def prepare_collection(self, collection):
        if collection is not None:
            self.collection = collection
        if self.collection is None:
            raise NotImplementedError("Please specify a mongodb collection!")
        self.col = self.collection

    @property
    def _col(self):
        import warnings
        warnings.warn(
            DeprecationWarning("this property will be deprecated soon!"))
        return self.collection

    def _default_is_duplicate(self, task):
        """
        Check if ``task.id`` presents in the collection.
        """
        return self.col.find_one({"_id": task.id}) is not None

    def _get_finished_id_set(self):
        """
        It's Primary key value set.
        """
        return set([
            doc["_id"] for doc in self.col.find({}, {"_id": True})
        ])

    def _default_post_process(self, task):
        """
        Save output_data into ``out`` field.
        """
        self.col.update(
            {"_id": task.id},
            {"$set": {self.output_key: self._encode(task.output_data)}},
            upsert=True,
        )

    def __len__(self):
        return self.col.find().count()

    def __iter__(self):
        for doc in self.col.find():
            yield doc["_id"]

    def clear_all(self):
        self.col.remove({})

    def get_output(self, input_data):
        key = self.user_hash_input(input_data)
        return self._decode(self.col.find_one({"_id": key})[self.output_key])

    def items(self):
        for doc in self.col.find():
            yield (doc["_id"], self._decode(doc[self.output_key]))
