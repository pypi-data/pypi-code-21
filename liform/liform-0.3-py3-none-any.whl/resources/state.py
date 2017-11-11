
class ResourceState(object):
    def __init__(self, path, type, name, id, code, ipv4, ipv6, state):
        self.path = path
        self.type = type
        self.name = name
        self.id = id
        self.code = code
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.state = state


class StateConnection(object):
    def __init__(self, path):
        self.__path = path
        self.__connection = None
        self.__cursor = None

    def __enter__(self):
        from sqlite3 import connect

        self.__connection = connect(self.__path)
        self.__connection.isolation_level = 'EXCLUSIVE'
        self.__cursor = self.__connection.cursor()

        return self

    def __exit__(self, type, value, traceback):
        self.__connection.commit()
        self.__connection.close()

    def execute(self, command, args={}):
        self.__cursor.execute(command, args)

    def fetchone(self):
        return self.__cursor.fetchone()

    def fetchall(self):
        return self.__cursor.fetchall()


class StateDatabase(object):
    def __init__(self, settings):
        from os.path import abspath

        self.__state_path = abspath(settings['database_state']['path'])

        with StateConnection(self.__state_path) as connection:
            connection.execute('PRAGMA main.auto_vacuum = FULL;')
            connection.execute('PRAGMA automatic_index = 1;')
            connection.execute('PRAGMA checkpoint_fullfsync = 1;')
            connection.execute('PRAGMA fullfsync = 1;')
            connection.execute('PRAGMA main.journal_mode = WAL;')
            connection.execute('PRAGMA main.schema_version = 0;')
            connection.execute('PRAGMA main.user_version = 0;')
            connection.execute('PRAGMA main.synchronous = EXTRA;')
            connection.execute('''
CREATE TABLE IF NOT EXISTS resource(
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    id INTEGER DEFAULT NULL,
    code TEXT DEFAULT NULL,
    ipv4 TEXT DEFAULT NULL,
    ipv6 TEXT DEFAULT NULL,
    state INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT resource_index_1 PRIMARY KEY(path)
    CONSTRAINT resource_index_2 UNIQUE(type, id));''')

    def get(self, path):
        with StateConnection(self.__state_path) as connection:
            connection.execute('''
SELECT
    path,
    type,
    name,
    id,
    code,
    ipv4,
    ipv6,
    state
FROM
    resource
WHERE
    path=:path''',
                               {'path': path})
            record = connection.fetchone()

        if record is None:
            return ResourceState(path, None, None, None, None, None, None, 0)

        return ResourceState(
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7])

    def set(self, path, type, name, id, code, ipv4, ipv6, state):
        with StateConnection(self.__state_path) as connection:
            if state == -1:
                connection.execute('''
DELETE FROM
    resource
WHERE
    (path = :path)''',
                                   {'path': path})
            else:
                connection.execute('''
INSERT OR REPLACE INTO
    resource
    (path, type, name, state)
VALUES
    (:path, :type, :name, :state)''',
                                   {
                                       'path': path,
                                       'type': type,
                                       'name': name,
                                       'state': state
                                   })

                if id:
                    connection.execute(
                        'UPDATE resource SET id = :id WHERE path = :path',
                        {'path': path, 'id': id})

                if code:
                    connection.execute(
                        'UPDATE resource SET code = :code WHERE path = :path',
                        {'path': path, 'code': code})

                if ipv4:
                    connection.execute(
                        'UPDATE resource SET ipv4 = :ipv4 WHERE path = :path',
                        {'path': path, 'ipv4': ipv4})

                if ipv6:
                    connection.execute(
                        'UPDATE resource SET ipv6 = :ipv6 WHERE path = :path',
                        {'path': path, 'ipv6': ipv6})

    def list(self):
        with StateConnection(self.__state_path) as connection:
            connection.execute('''
SELECT
    path,
    type,
    name,
    id,
    code,
    ipv4,
    ipv6,
    state
FROM
    resource
ORDER BY
    path''')

        resources = []

        for record in connection.fetchall():
            resources.append(
                ResourceState(
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    record[7]))

        return resources
