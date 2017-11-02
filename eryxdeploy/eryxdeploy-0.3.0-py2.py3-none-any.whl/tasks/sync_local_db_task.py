# coding=utf-8
import os

from fabric.context_managers import settings
from fabric.state import env
from fabric.tasks import Task

from eryx_deploy.utils.interactive_console import InteractiveConsole


class SyncLocalDBTask(Task):
    """
    Syncs your local DB in your dev machine with a remote stack DB
    """
    name = 'sync_local_db'

    def run(self):
        remote_stack = env.stacks[env.env]
        local_stack = env.local_stack

        if remote_stack.host_machine().exists_a_db_dump_from_today(remote_stack.db().name()):
            question = "There's a already a DB dump from today. Do you want to create another one now?"
            if InteractiveConsole.yes_or_no(question, default=True):
                remote_stack.host_machine().create_db_dump_of(remote_stack.db())

        else:
            remote_stack.host_machine().create_db_dump_of(remote_stack.db())

        db_dump_filename = self._get_latest_db_dump_from_server(remote_stack, local_stack.host_machine())

        self._reload_local_db_from_dump(local_stack, db_dump_filename)

    # private

    def _get_latest_db_dump_from_server(self, remote_stack, local_workstation):
        dump_filename = remote_stack.host_machine().latest_db_dump_filename(database_name=remote_stack.db().name())
        remote_dump_path = os.path.join('~/', dump_filename)
        local_dump_path = os.path.join('./', dump_filename)

        if local_workstation.path_exists(local_dump_path):
            InteractiveConsole.show_info("There's already a local dump file with the same name, nothing to download.")
            return local_dump_path
        else:
            InteractiveConsole.show_info(
                "Downloading remote DB dump file %s to working directory..." % dump_filename)
            files_downloaded = remote_stack.host_machine().get(remote_dump_path, local_path='./')

            if remote_dump_path in files_downloaded.failed:
                return InteractiveConsole.abort(
                    "There was a problem downloading file %s. Aborting." % remote_dump_path)
            else:
                return files_downloaded[0]

    # TODO: Move this to Database class. It should warn MUCH MORE if DB is remote instead of local!
    def _reload_local_db_from_dump(self, local_stack, dump_filename):
        if local_stack.host_machine().path_exists(dump_filename):
            if InteractiveConsole.yes_or_no("Your local DB will be DELETED. Do you want to continue?", default=False):
                with settings(warn_only=True):
                    result = local_stack.db().drop_db()
                    InteractiveConsole.show_info(result.return_code)

                local_stack.db().create()
                local_stack.db().load_dump(dump_input_path=dump_filename)
            else:
                InteractiveConsole.abort()
        else:
            InteractiveConsole.abort("File %s not found! Aborting." % dump_filename)
