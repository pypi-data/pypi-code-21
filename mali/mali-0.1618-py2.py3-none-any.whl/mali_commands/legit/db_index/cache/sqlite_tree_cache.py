# coding=utf-8
from ...connection_mixin import ConnectionMixin
from .tree_cache import TreeCache


class SqliteTreeCache(ConnectionMixin, TreeCache):
    create_tree_sql = """
      CREATE TABLE
      IF NOT EXISTS tree (
        name TEXT PRIMARY KEY,
        files BLOB,
        sha TEXT
      );
    """

    def __init__(self, connection):
        super(SqliteTreeCache, self).__init__(connection)
        self._create_table_if_needed()

    def _create_table_if_needed(self):
        with self._connection.get_cursor() as c:
            self._connection.execute_multi(c, self.create_tree_sql)
            self._connection.commit()

    def _set_files(self, trees_objects):
        import sqlite3

        inserts = []
        for path, tree in trees_objects.items():
            blob = '\n'.join(self.build_blob(tree))

            inserts.append((path.decode('utf8'), sqlite3.Binary(blob.encode('utf8')), tree.id.decode('utf8')))

        with self._connection.get_cursor() as c:
            c.executemany('INSERT OR REPLACE INTO [tree] (name, files, sha) VALUES (?, ?, ?)', inserts)

    @classmethod
    def decode_sqlite_to_str(cls, val):
        return str(val)

    def _get_files(self, scans):
        with self._connection.get_cursor() as c:
            params = ",".join(['?'] * len(scans))
            paths = [path.decode('utf8') for path, _, _ in scans]
            c.execute("select [name], [files] from tree where [name] in (%s)" % params, paths)
            files_data = c.fetchall()
            return {self.decode_sqlite_to_str(files_row['name']): self._files_sha_array_to_dict(self.decode_sqlite_to_str(files_row['files'])) for files_row in files_data}

    def get_commit_id(self):
        with self._connection.get_cursor() as c:
            c.execute("select [sha] from [tree] where [name] = ? limit 1", ('', ))
            files_data = c.fetchone()

            commit_id = files_data['sha']

            return commit_id.encode('utf8')
