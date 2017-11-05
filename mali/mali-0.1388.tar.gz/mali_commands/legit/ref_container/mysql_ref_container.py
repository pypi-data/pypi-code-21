# coding=utf-8
from ..connection_mixin import ConnectionMixin
from ..dulwich.refs import RefsContainer

SYMREF = b'ref: '


class MySqlRefsContainer(ConnectionMixin, RefsContainer):
    create_refs_sql = """
      CREATE TABLE
      IF NOT EXISTS refs (
        name VARCHAR(256) PRIMARY KEY,
        data TEXT
      );
    """

    def __init__(self, connection):
        super(MySqlRefsContainer, self).__init__(connection)
        self._create_table_if_needed()

    def get_packed_refs(self):
        return {}

    def read_loose_ref(self, name):
        """Read a reference and return its contents.

        If the reference file a symbolic reference, only read the first line of
        the file. Otherwise, only read the first 40 bytes.

        :param name: the refname to read, relative to refpath
        :return: The contents of the ref file, or None if the file does not
            exist.
        """

        with self._connection.get_cursor() as c:
            c.execute('SELECT data FROM refs WHERE name = %s LIMIT 1', (name,))
            data = c.fetchall()

        if len(data) == 0:
            return None

        data = data[0][0]

        header = data[:len(SYMREF)]
        if header == SYMREF:
            # Read only the first line
            return data.splitlines()[0]

        # Read only the first 40 bytes
        return data[:40].encode('ascii')

    def set_if_equals(self, name, old_ref, new_ref):
        """Set a refname to new_ref only if it currently equals old_ref.

        This method follows all symbolic references, and can be used to perform
        an atomic compare-and-swap operation.

        :param name: The refname to set.
        :param old_ref: The old sha the refname must refer to, or None to set
            unconditionally.
        :param new_ref: The new sha the refname will refer to.
        :return: True if the set was successful, False otherwise.
        """

        self._check_refname(name)
        try:
            real_names, _ = self.follow(name)
            real_name = real_names[-1]
        except (KeyError, IndexError):
            real_name = name

        real_name = real_name.decode('ascii')
        old_ref = old_ref.decode('ascii')
        new_ref = new_ref.decode('ascii')

        update_sql = """
            UPDATE refs SET data = %(new_data)s WHERE name = %(name)s AND data = %(old_data)s
        """

        if old_ref is not None:
            with self._connection.get_cursor() as c:
                c.execute(update_sql, dict(name=real_name, new_data=new_ref, old_data=old_ref))
                self._connection.commit()

        return True

    def add_if_new(self, name, ref):
        update_sql = """
            INSERT INTO refs (name, data)
            SELECT * FROM (SELECT %(name)s, %(data)s) AS tmp
            WHERE NOT EXISTS (
                SELECT name FROM refs WHERE name = %(name)s
            ) LIMIT 1;
        """
        self._check_refname(name)

        name = name.decode('ascii')
        ref = ref.decode('ascii')

        with self._connection.get_cursor() as c:
            c.execute(update_sql, dict(name=name, data=ref))
            self._connection.commit()

        return True

    def remove_if_equals(self, name, old_ref):
        raise NotImplementedError()

    def _create_connection(self, **kwargs):
        import mysql.connector

        user = kwargs.get('user')
        password = kwargs.get('password')
        host = kwargs.get('host')
        database = kwargs.get('database')

        return mysql.connector.connect(user=user, password=password, host=host, database=database)

    def _create_table_if_needed(self):
        with self._connection.get_cursor() as c:
            c.execute(self.create_refs_sql)
            self._connection.commit()
