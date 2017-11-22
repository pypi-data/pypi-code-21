# coding=utf-8
from .base_db_index import BaseMLIndex


class MySqlMLIndex(BaseMLIndex):
    create_index_sql = """
      CREATE TABLE
      IF NOT EXISTS files (
        name varchar(256) PRIMARY KEY,
        sha text not null,
        ctime integer not null,
        mtime integer not null,
        mode integer not null,
        uid integer not null,
        gid integer not null,
        size integer not null
      );
    """

    def __init__(self, connection):
        super(MySqlMLIndex, self).__init__(connection)

    def remove_path(self, name):
        with self._connection.get_cursor() as c:
            c.execute("DELETE from files where name=%s limit 1", (name.decode('utf8'), ))
            self._connection.commit()

    def set_entries(self, entries):
        values = self._decode_entries(entries)

        with self._connection.get_cursor() as c:
            c.executemany("REPLACE INTO files (name, sha, ctime, mtime, mode, uid, gid, size) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", values)
            self._connection.commit()

    def _create_table_if_needed(self):
        with self._connection.get_cursor() as c:
            c.execute(self.create_index_sql)
            self._connection.commit()

    def iterblobs(self):
        with self._connection.get_cursor() as c:
            c.execute('SELECT name, sha, mode FROM files order by name')
            for row in c:
                yield row[0].encode('utf8'), row[1].encode('utf8'), row[2]

    def commit(self, object_store):
        from dulwich.index import commit_tree

        return commit_tree(object_store, self.iterblobs())
