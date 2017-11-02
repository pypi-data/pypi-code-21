class Database(object):
    def __init__(self, client_machine, server_machine, name, port, user, password):
        self._client_machine = client_machine
        self._server_machine = server_machine
        self._port = port
        self._name = name
        self._user = user
        self._password = password

    def host(self):
        if self._client_machine == self._server_machine:
            return 'localhost'
        else:
            return self._server_machine.hostname()

    def port(self):
        return self._port

    def name(self):
        return self._name

    def user(self):
        return self._user

    def password(self):
        return self._password

    @staticmethod
    def engine():
        raise NotImplementedError('Subclass responsibility.')

    def drop_db(self):
        raise NotImplementedError('Subclass responsibility.')

    def create(self):
        if not self._db_exists():
            self._create_db()

    def dump(self, backup_file_path):
        raise NotImplementedError('Subclass responsibility.')

    def load_dump(self, backup_file_path):
        raise NotImplementedError('Subclass responsibility.')

    def install_server(self):
        raise NotImplementedError('Subclass responsibility.')

    def install_client(self):
        raise NotImplementedError('Subclass responsibility.')

    # private

    def _create_db(self):
        raise NotImplementedError('Subclass responsibility.')

    def _db_exists(self):
        raise NotImplementedError('Subclass responsibility.')
