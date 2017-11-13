# coding=utf-8
from contextlib import closing
from .base_db_index import BaseMLIndex
from .cache import SqliteTreeCache


class SqliteMLIndex(BaseMLIndex):
    create_index_sql = """
      CREATE TABLE
      IF NOT EXISTS files (
        name text PRIMARY KEY,
        sha text not null,
        ctime integer not null,
        mtime integer not null,
        mode integer not null,
        uid integer not null,
        gid integer not null,
        size integer not null
      );
    """

    def __init__(self, connection, **kwargs):
        self.__tree_cache = SqliteTreeCache(connection)
        super(SqliteMLIndex, self).__init__(connection)

    def tree_cache(self):
        return self.__tree_cache

    def remove_path(self, name):
        with closing(self._conn.cursor()) as c:
            c.execute("DELETE from files where name=? limit 1", (name.decode('utf8'), ))
            self._conn.commit()

    def set_entries(self, entries):
        values = self._decode_entries(entries)

        with self._connection.get_cursor() as c:
            c.executemany("INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)

            self.__tree_cache.set_entries(entries)

            self._connection.commit()

    def _create_table_if_needed(self):
        with self._connection.get_cursor() as c:
            self._connection.execute_multi(c, self.create_index_sql)
            self._connection.commit()

    def write(self):
        pass

    def iterblobs(self):
        with self._connection.get_cursor() as c:
            c.execute('SELECT name, sha, mode FROM files order by name')
            for row in c:
                yield row['name'].encode('utf8'), row['sha'].encode('utf8'), row['mode']

    def commit(self, object_store):
        from dulwich.index import commit_tree

        return commit_tree(object_store, self.iterblobs())

    def get_commit_id(self):
        return self.__tree_cache.get_commit_id()
