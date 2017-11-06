# coding=utf-8
from .base_db_index import BaseMLIndex


class SpannerMLIndex(BaseMLIndex):
    create_index_ddl = """
      CREATE TABLE files (
        name String(256) NOT NULL,
        sha String(256) NOT NULL,
        ctime INT64	NOT NULL,
        mtime INT64	NOT NULL,
        mode INT64 NOT NULL,
        uid INT64 NOT NULL,
        gid INT64 NOT NULL,
        size INT64 NOT NULL
      ) PRIMARY KEY (name)
    """

    def set_entries(self, entries):
        values = self._decode_entries(entries)

        with self._connection.get_cursor() as database:
            with database.batch() as batch:
                batch.insert(
                    table='files',
                    columns=('name', 'sha', 'ctime', 'mtime', 'mode', 'uid', 'gid', 'size', ),
                    values=values)

    def _create_table_if_needed(self):
        with self._connection.get_cursor() as c:
            c.update_ddl([self.create_index_ddl])

    def __init__(self, connection):
        super(SpannerMLIndex, self).__init__(connection)
