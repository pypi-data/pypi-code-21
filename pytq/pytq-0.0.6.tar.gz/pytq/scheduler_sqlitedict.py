#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .pkg import sqlitedict
    from .scheduler import Task, BaseDBTableBackedScheduler, Encoder
except:  # pragma: no cover
    from pytq.pkg import sqlitedict
    from pytq.scheduler import Task, BaseDBTableBackedScheduler, Encoder


class SqliteDictScheduler(BaseDBTableBackedScheduler, Encoder):
    """
    A sqlite database backed scheduler. The primary key field is for
    fingerprint of input data, another field for output data.
    """
    user_db_path = None

    def __init__(self, logger=None, user_db_path=None):
        super(SqliteDictScheduler, self).__init__(logger=logger)

        self.link_encode_method()

        # initiate back end database
        self._dct = sqlitedict.SqliteDict(
            self.user_db_path, autocommit=True,
            encode=self._encode,
            decode=self._decode,
        )

    @property
    def user_db_path(self):
        """
        Back-end sqlite database file path.
        """
        raise NotImplementedError

    def _default_is_duplicate(self, task):
        """
        Check if ``task.id`` is presents in primary_key column.
        """
        return task.id in self._dct

    def _get_finished_id_set(self):
        """
        It's Primary key value set.
        """
        return set(self._dct.keys())

    def _default_post_process(self, task):
        """
        Write serialized output_data to another column.
        """
        self._dct[task.id] = task.output_data

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)

    def clear_all(self):
        self._dct.clear()

    def get(self, id):
        return self._dct.get(id)
