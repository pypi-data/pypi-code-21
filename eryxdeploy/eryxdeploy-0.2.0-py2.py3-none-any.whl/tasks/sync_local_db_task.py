# coding=utf-8
import os

from fabric.colors import red
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.operations import get
from fabric.tasks import Task
from fabric.utils import puts


class SyncLocalDBTask(Task):
    """
    NOTE: Untested. Use at your own risk!
    """

    name = 'sync_local_db'

    def __init__(self, server, local_workstation, remote_db, local_db):
        self._server = server
        self._local_workstation = local_workstation
        self._remote_db = remote_db
        self._local_db = local_db
        super(SyncLocalDBTask, self).__init__()

    def run(self):
        if self._server.exists_a_db_dump_from_today(self._remote_db.name()):
            question = "Ya existe un backup de la base de datos remota con fecha de hoy ¿Quieres crear uno de todas " \
                       "formas? "
            answer = confirm(question, default=True)

            if answer:
                self._server.create_db_dump_of(self._remote_db)

        else:
            self._server.create_db_dump_of(self._remote_db)

        db_dump_filename = self._download_latest_remote_db_dump()

        self._reload_local_db_from_dump(db_dump_filename)

    # private

    def _download_latest_remote_db_dump(self):
        backup_file_name = self._server.latest_db_dump_filename(database_name=self._remote_db.name())
        backup_file_path = os.path.join('./', backup_file_name)
        possible_local_back_up_file = os.path.join('./', backup_file_name)

        if self._local_workstation.path_exists(possible_local_back_up_file):
            puts("Ya existe un archivo con el mismo nombre, asumiendo que es el backup deseado...")
            return possible_local_back_up_file

        puts("Descargando base de datos remota...")
        files_downloaded = get(backup_file_path, local_path='./')

        if backup_file_path in files_downloaded.failed:
            self._local_workstation.abort("Problema al descargar el archivo %s!" % backup_file_path)

        return files_downloaded[0]

    def _reload_remote_db_from_file(self, dump_filename):
        question = "SI CONTINUA CON ESTA OPERACIÓN SE ELIMINARÁ LA BASE DE DATOS REMOTA. ¿Desea continuar?"
        answer_1 = confirm(red(question), default=False)

        question = "!!!!!SI CONTINUA CON ESTA OPERACIÓN SE ELIMINARÁ LA BASE DE DATOS REMOTA. ¿Esta muy seguro de que " \
                   "desea continuar? "
        answer_2 = confirm(red(question), default=False)

        remote_file_path = os.path.join('./', dump_filename)

        if answer_1 and answer_2:
            self._remote_db.drop_db()
            self._remote_db.create()
            self._remote_db.rebuild_from_backup(remote_file_path)
        else:
            self._server.abort()

    def _reload_local_db_from_dump(self, dump_filename):
        if self._local_workstation.path_exists(dump_filename):
            if confirm("La base de datos local será borrada. Desea continuar?", default=False):
                with settings(warn_only=True):
                    result = self._local_db.drop_db()
                    puts(result.return_code)

                self._local_db.create()
                self._local_db.rebuild_from_backup(backup_file_path=dump_filename)
            else:
                self._local_workstation.abort()
        else:
            self._local_workstation.abort("No se encontro el archivo %s!" % dump_filename)
