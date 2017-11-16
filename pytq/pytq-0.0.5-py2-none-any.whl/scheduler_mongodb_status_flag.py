#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from .scheduler import StatusFlag
from .scheduler_mongodb import MongoDBScheduler


class MongoDBStatusFlagScheduler(MongoDBScheduler, StatusFlag):
    """
    Similar to :class:`~pytq.scheduler_mongodb.MongoDBScheduler`.

    New Feature:

    There's pre-defined integer - ``duplicate_flag``, will be stored in
    ``status`` field. there's a ``edit_at`` datetime field, represent the
    last time the document been edited.

    .. note::

        Any value greater or equal than ``duplicate_flag``, AND the ``edit_at``
        time is smaller ``update_interval`` seconds ago, means it is a duplicate
        item.

    :param duplicate_flag: int, represent a status code for finished / duplicate
    :param update_interval: int, represent need-to-update interval (unit: seconds)
    """

    def __init__(self, logger=None, collection=None,
                 duplicate_flag=None, update_interval=None):
        super(MongoDBStatusFlagScheduler, self). \
            __init__(logger=logger, collection=collection)
        self.pre_process_duplicate_flag_and_update_interval(
            duplicate_flag, update_interval,
        )

    def _default_is_duplicate(self, task):
        """
        Check the status flag is greater or equal than
        :attr:`~StatusFlagScheduler.duplicate_flag` and last edit time is with
        in recent :attr:`~StatusFlagScheduler.update_interval` seconds.
        """
        n_sec_ago = datetime.utcnow() - timedelta(seconds=self.update_interval)
        filters = {
            "_id": task.id,
            self.status_key: {"$gte": self.duplicate_flag},
            self.edit_at_key: {
                "$gte": n_sec_ago,
            },
        }
        return self._col.find_one(filters) is not None

    def _get_finished_id_set(self):
        """
        It's Primary key value set.
        """
        n_sec_ago = datetime.utcnow() - timedelta(seconds=self.update_interval)
        filters = {
            self.status_key: {"$gte": self.duplicate_flag},
            self.edit_at_key: {
                "$gte": n_sec_ago,
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
                    self.output_key: self._encode(task.output_data),
                    self.status_key: self.duplicate_flag,
                    self.edit_at_key: datetime.utcnow(),
                },
            },
            upsert=True,
        )
