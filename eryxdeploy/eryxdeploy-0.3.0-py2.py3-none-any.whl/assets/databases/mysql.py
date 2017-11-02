from eryx_deploy.assets.databases.abs_database import Database


class MySqlDatabase(Database):
    """
    NOTE: Untested. Use with caution! Needs adjustments for remote use for sure!
    """

    @staticmethod
    def engine():
        return 'mysql'

    def drop_db(self):
        return self._client_machine.run("sudo mysqladmin -p drop %s" % self._name)

    def dump(self, backup_file_path):
        self._client_machine.run(
            'mysqldump -u %s -p%s %s | gzip > %s' % (self._user, self._password, self._name, backup_file_path))

    def load_dump(self, backup_file_path):
        self._client_machine.run(
            "gunzip -c %(backup_file_path)s | sudo mysql -p %(db)s" % {'backup_file_path': backup_file_path,
                                                                       'db': self._name})

    def install_server(self):
        self._server_machine.install_mysql_server()

    def install_client(self):
        self._server_machine.install_mysql_client()

    # private

    def _create_db(self):
        self._client_machine.run("sudo mysqladmin -p create %s" % self._name)

    def _db_exists(self):
        raise NotImplementedError("Not implemented yet! Please do it :)")
