#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from .scheduler_mongodb import MongoDBScheduler


class StatusFlagScheduler(MongoDBScheduler):
    """
    MongoDB collection backed scheduler.

    Feature:

    1. fingerprint of :meth:`~MongoDBScheduler._hash_input()` will be ``_id``
      field in MongoDB collection.
    2. output_data will be serialized and stored in ``out`` field.
    3. there's pre-defined integer - ``duplicate_flag``, will be stored in
      ``status`` field. there's a ``edit_at`` datetime field, represent the
      last time the document been edited.

    .. note::

        Any value greater or equal than ``duplicate_flag``, AND the ``edit_at``
        time is smaller ``update_interval`` seconds ago, means it is a duplicate
        item.

    :param logger: A :class:`loggerFactory.logger.BaseLogger` instance.
    :param collection: :class:`pymongo.Collection` instance.
    :param duplicate_flag: int, represent a status code for finished / duplicate
    :param update_interval: int, represent need-to-update interval (unit: seconds)
    """
    duplicate_flag = None  # integer
    """
    A integer value represent its a duplicate item. Any value greater or equal 
    than this will be a duplicate item, otherwise its not.

    You could define that when you initiate the scheduler.
    """

    update_interval = None  # integer, represent xxx seconds
    """
    If a item has been finished more than ``update_interval`` seconds, then
    it should be re-do, and it is NOT a duplicate item.

    You could define that when you initiate the scheduler. 
    """

    status_key = "_status"
    edit_at_key = "_edit_at"

    def __init__(self, logger=None, collection=None,
                 duplicate_flag=None, update_interval=None):
        super(StatusFlagScheduler, self). \
            __init__(logger=logger, collection=collection)
        if duplicate_flag is not None:
            self.duplicate_flag = duplicate_flag
        if update_interval is not None:
            self.update_interval = update_interval

    @property
    def duplicate_flag(self):
        """
        A integer value represent its a duplicate item. Any value greater or equal
        than this will be a duplicate item, otherwise its not.

        You could define that when you initiate the scheduler.
        """
        raise NotImplementedError

    @property
    def update_interval(self):
        """
        If a item has been finished more than ``update_interval`` seconds, then
        it should be re-do, and it is NOT a duplicate item.

        You could define that when you initiate the scheduler.
        """
        raise NotImplementedError

    def _default_is_duplicate(self, task):
        """
        Check the status flag is greater or equal than
        :attr:`~StatusFlagScheduler.duplicate_flag` and last edit time is with
        in recent :attr:`~StatusFlagScheduler.update_interval` seconds.
        """
        filters = {
            "_id": task.id,
            self.status_key: {"$gte": self.duplicate_flag},
            self.edit_at_key: {
                "$gte": (
                    datetime.utcnow() - timedelta(seconds=self.update_interval)),
            },
        }
        return self._col.find_one(filters) is not None

    def _get_finished_id_set(self):
        """
        It's Primary key value set.
        """
        filters = {
            self.status_key: {"$gte": self.duplicate_flag},
            self.edit_at_key: {
                "$gte": (
                    datetime.utcnow() - timedelta(
                        seconds=self.update_interval)),
            },
        }
        wanted = {"_id": True}
        return set([
            doc["_id"] for doc in self._col.find(filters, wanted)
        ])

    def _default_post_process(self, task):
        """
        Save output_data into ``out`` field.
        """
        self._col.update(
            {"_id": task.id},
            {
                "$set": {
                    "out": self._encode(task.output_data),
                    self.status_key: self.duplicate_flag,
                    self.edit_at_key: datetime.utcnow(),
                },
            },
            upsert=True,
        )
