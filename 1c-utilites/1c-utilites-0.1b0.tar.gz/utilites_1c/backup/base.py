# =*= coding: utf-8 =*=
from __future__ import unicode_literals
import os
import sys
import time
import logging
import subprocess
from configparser import ConfigParser

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.DEBUG
)


class BaseBackupBackend(object):
    DEFAULT_NAME_MASK = '1c-backup'

    def __init__(self, args):
        self.args = args
        self.config = self.get_config(self.args.config)
        self.backups_dir = self.config.get(
            "main", "backups_dir", fallback="/tmp/"
        ) + "/"
        self.backups_files = self.config.getint("main", "last", fallback=5)

    @property
    def file_name(self):
        file_name = self.backups_dir
        file_name += "{}-{}.gz".format(
            self.DEFAULT_NAME_MASK, int(time.time())
        )
        return file_name

    def get_config(self, config_name='/etc/1c/backup.ini'):
        config = ConfigParser()
        logging.debug("Read config " + config_name)
        config.read([config_name])
        return config

    def get_backups_list(self):
        return sorted([
            f for f in os.listdir(self.backups_dir)
            if self.DEFAULT_NAME_MASK in f and f[-3:] == '.gz'
        ])

    def remove_older(self):
        counter = 0
        for file in reversed(self.get_backups_list()):
            if counter >= self.backups_files:
                logging.info("Removed: {}".format(self.backups_dir + file))
                os.remove(self.backups_dir + file)
            counter += 1

    def execute(self, execute_string):
        return subprocess.check_output(
            ["bash", "-c", execute_string], stderr=subprocess.STDOUT
        )

    def backup_operation(self):
        execute_string = self._generate_backup_string()
        logging.info("Executes: " + execute_string)
        self.execute(execute_string)
        self.remove_older()

    def backup(self):
        try:
            self.backup_operation()
            logging.debug("Current backups = " + str(self.get_backups_list()))
        except subprocess.CalledProcessError as err:
            logging.error("Code: {} - {}".format(err.returncode, err.output))
            sys.exit(-1)
        except Exception as err:
            logging.critical(err)
            sys.exit(-1)

    def _generate_backup_string(self):
        raise NotImplementedError
