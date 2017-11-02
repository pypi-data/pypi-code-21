#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .pkg import sqlitedict
    from .scheduler import Task, BaseDBTableBackedScheduler
except:  # pragma: no cover
    from pytq.pkg import sqlitedict
    from pytq.scheduler import Task, BaseDBTableBackedScheduler


class SqliteDictScheduler(BaseDBTableBackedScheduler):
    user_db_path = None

    def __init__(self, logger=None, user_db_path=None):
        super(SqliteDictScheduler, self).__init__(logger=logger)

        # link encode method
        try:
            self.user_encode(None)
            encode = self.encode
        except NotImplementedError:
            encode = sqlitedict.encode
        except:
            encode = self.encode

        # link decode method
        try:
            self.user_decode(None)
            decode = self.decode
        except NotImplementedError:
            decode = sqlitedict.decode
        except:
            decode = self.decode

        # initiate back end database
        self._dct = sqlitedict.SqliteDict(
            self.user_db_path, autocommit=True,
            encode=encode,
            decode=decode,
        )

    @property
    def user_db_path(self):
        """
        Back-end sqlite database file path.
        """
        raise NotImplementedError

    def user_encode(self, obj):
        """
        (Optional) User defined serializer for output_data.

        :returns: bytes or string.

        **中文文档**

        用于对处理结果序列化的函数。默认使用pickle。
        """
        raise NotImplementedError

    def user_decode(self, bytes_or_str):
        """
        (Optional) User defined deserializer for output_data.

        :returns: python object.

        **中文文档**

        用于对处理结果反序列化的函数。默认使用pickle。
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
