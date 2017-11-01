# coding=utf-8
from abc import ABCMeta, abstractmethod
from contextlib import closing
from ..connection_mixin import ConnectionMixin


class BaseMLIndex(ConnectionMixin):
    __metaclass__ = ABCMeta

    def __init__(self, connection):
        super(BaseMLIndex, self).__init__(connection)

        self._create_table_if_needed()

    def _get_hash_by_name_query(self):
        pass

    def get_hash_by_name(self, name):
        with closing(self._conn.cursor()) as c:
            c.execute(self._get_hash_by_name_query(), (name.decode('utf8'), ))

            result = c.fetchone()
            return result[0].encode('utf8') if result is not None else None

    @abstractmethod
    def _create_table_if_needed(self):
        """

        :return:
        """

    @abstractmethod
    def begin_commit(self, tree_id):
        """

        :return:
        """

    @abstractmethod
    def end_commit(self):
        """

        :return:
        """

    @classmethod
    def _decode_entries(cls, entries):
        values = []
        for name, entry in entries.items():
            ctime, mtime, dev, ino, mode, uid, gid, size, sha, flags, url = entry

            name = name.decode('utf8')
            sha = sha.decode('utf8')

            row = (name, sha, ctime, mtime, mode, uid, gid, size, url)

            values.append(row)

        return values
