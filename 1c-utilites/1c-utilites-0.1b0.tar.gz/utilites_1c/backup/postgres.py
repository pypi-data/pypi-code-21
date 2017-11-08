# =*= coding: utf-8 =*=
from __future__ import unicode_literals
import gzip
from .base import BaseBackupBackend, os


class BackupBackendPostgres(BaseBackupBackend):
    CONFIG_PARAMS = {
        "-h": "host",
        "-p": "port",
        "-d": "db",
        "-P": "password",
        "-U": "user"
    }

    def _format_op_sting(self, op_string, key, name):
        if self.config.get("postgres", name, fallback=""):
            if name == "password":
                os.putenv("PGPASSWORD", self.config.get("postgres", name))
            elif name == "db":
                op_string += ' "{}"'.format(self.config.get("postgres", name))
            else:
                op_string += " {} {}".format(
                    key, self.config.get("postgres", name)
                )
        return op_string

    def _generate_backup_string(self):
        op_string = "pg_dump"
        for param, name in self.CONFIG_PARAMS.items():
            op_string = self._format_op_sting(op_string, param, name)
        op_string += " -F c -b "
        return op_string

    def archive_backup(self, output):
        with gzip.open(self.file_name, "w") as file:
            file.write(output)

    def execute(self, execute_string):
        output = super(BackupBackendPostgres, self).execute(execute_string)
        self.archive_backup(output)
