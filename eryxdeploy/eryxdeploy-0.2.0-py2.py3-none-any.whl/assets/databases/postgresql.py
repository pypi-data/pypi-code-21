from eryx_deploy.assets.databases.abs_database import Database


class PostgresDatabase(Database):
    @staticmethod
    def engine():
        return 'postgresql'

    def drop_db(self):
        self._client_machine.run("PGPASSWORD='%(password)s' "
                                 "dropdb -h %(host)s -U %(user)s %(db)s" % {'db': self.name(),
                                                                            'host': self.host(),
                                                                            'user': self.user(),
                                                                            'password': self.password()})

    def backup(self, backup_file_path):
        self._client_machine.run(
            "PGPASSWORD='%(password)s' "
            "pg_dump -h %(host)s -U %(user)s %(db)s | gzip > %(file)s" % {'db': self.name(),
                                                                          'host': self.host(),
                                                                          'user': self.user(),
                                                                          'password': self.password(),
                                                                          'file': backup_file_path})

    def rebuild_from_backup(self, backup_file_path):
        self._client_machine.run(
            "PGPASSWORD='%(password)s' "
            "gunzip -c %(file)s | psql -h %(host)s -U %(user)s %(db)s" % {'db': self.name(),
                                                                          'host': self.host(),
                                                                          'user': self.user(),
                                                                          'password': self.password(),
                                                                          'file': backup_file_path})

    def install_server(self):
        self._server_machine.install_postgresql_server(master_username=self.user(), master_password=self.password())

    def install_client(self):
        self._client_machine.install_postgresql_client()

    # private

    def _create_db(self):
        self._client_machine.run(
            "PGPASSWORD='%(password)s' createdb -h %(host)s -U %(user)s %(db)s --owner %(user)s" % {
                'db': self.name(),
                'host': self.host(),
                'user': self.user(),
                'password': self.password()})

    def _db_exists(self):
        res = self._client_machine.run_check(
            '''PGPASSWORD="%(password)s" psql -h %(host)s -U %(user)s -d %(db)s -c ""'''
            % {'host': self.host(), 'db': self.name(), 'user': self.user(), 'password': self.password()},
            message="Checking if PostgreSQL db '%s' exists ..." % self.name())
        return res.succeeded
