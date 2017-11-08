# =*= coding: utf-8 =*=
from __future__ import unicode_literals
import os
from .base import BaseBackupBackend


class BackupBackendFile(BaseBackupBackend):
    def _check_base(self, base_path):
        files_in_base = os.listdir(base_path)
        for file in files_in_base:
            if ".1CD" in file:
                return
        raise Exception("Dir without database (*.1CD) file")

    def _generate_backup_string(self):
        base_path = self.config.get("file", "base_path", fallback="")
        self._check_base(base_path)
        op_string = "tar -zcvf"
        op_string += " " + self.file_name
        op_string += " " + base_path
        return op_string
