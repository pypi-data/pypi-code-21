class Machine(object):
    """
    An abstract machine
    """

    def __init__(self, hostname):
        self._hostname = hostname

    def install_postgresql_server(self, master_username, master_password):
        raise NotImplementedError('Subclass responsibility')

    def install_mysql_server(self):
        raise NotImplementedError('Subclass responsibility')

    def hostname(self):
        return self._hostname
