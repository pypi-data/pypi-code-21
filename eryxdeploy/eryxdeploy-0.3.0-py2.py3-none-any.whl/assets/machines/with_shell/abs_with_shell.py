import os

from fabric.colors import yellow
from fabric.context_managers import settings, lcd, cd, prefix
from fabric.contrib.files import append, contains, exists
from fabric.operations import local, run, get
from fabric.state import env

from eryx_deploy.assets.abs_executable_environment import ExecutableEnvironment
from eryx_deploy.assets.machines.abs_machine import Machine
from eryx_deploy.utils.interactive_console import InteractiveConsole


class MachineWithShell(Machine, ExecutableEnvironment):
    """
    A machine that can be accessed through SSH
    """

    # constructors

    @classmethod
    def new_remote(cls, hostname, ssh_connection, project_path):
        """
        Creates a remote machine which will be accessed through SSH from your machine.

        :param hostname: Machine hostname
        :param ssh_connection: A SSH connection string like 'root@server.com'. Can also be a Host name found
        on ~/.ssh/config
        :param project_path: Absolute path where to store project
        :return: A remote machine with a shell
        """
        return cls(hostname=hostname, ssh_connection=ssh_connection, project_path=project_path, is_local=False)

    @classmethod
    def new_local(cls, project_path):
        return cls(hostname='localhost', project_path=project_path, ssh_connection=None, is_local=True)

    # initialization

    def __init__(self, hostname, ssh_connection, project_path, is_local):
        super(MachineWithShell, self).__init__(hostname=hostname)
        self._ssh_connection = ssh_connection
        self._project_path = project_path
        self._is_local = is_local

    # getters

    def project_path(self):
        return self._project_path

    # ExecutableEnvironment protocol

    def first_time_setup(self):
        pass

    def run(self, command, on_fail_msg=None):
        if env.confirm_before_run:
            confirm_text = "Should I run '%s' on '%s'?" % (command, self.hostname())
            if env.cwd:
                confirm_text += " (working dir: %s)" % env.cwd
            execution_confirmed = InteractiveConsole.yes_or_no(confirm_text)
        else:
            execution_confirmed = True

        if execution_confirmed:
            if on_fail_msg:
                with settings(warn_only=True):
                    result = self._run(command)

                    if result.failed:
                        InteractiveConsole.abort_with_suggestion(message=on_fail_msg)
                    else:
                        return result
            else:
                return self._run(command)
        else:
            if not env.allow_skipping_cmd or InteractiveConsole.yes_or_no('Should I abort execution now?'):
                InteractiveConsole.abort("OK! Stopping execution now.")

    # operations

    def run_check(self, command, message):
        """
        Run a command that can fail, to check the return value

        @param command: Command to run
        @param message: Message shown to the user informing what the command is checking
        @return: Command output (like Fabric's run/sudo)
        """

        with settings(warn_only=True):
            InteractiveConsole.show_info(yellow(message))
            return self._run(command)

    def append(self, filename, text, use_sudo=False):
        if self._is_local:
            raise RuntimeError("This a local machine, cannot use Fabric's 'append' command which is remote.")
        else:
            return self._remote_op(append, filename, text, use_sudo=use_sudo)

    def contains(self, filename, text, use_sudo=False):
        if self._is_local:
            raise RuntimeError("This a local machine, cannot use Fabric's 'contains' command which is remote.")
        else:
            return self._remote_op(contains, filename=filename, text=text, use_sudo=use_sudo)

    def path_exists(self, path):
        InteractiveConsole.show_info("Checking if %s exists on %s ..." % (path, self.hostname()))

        if self._is_local:
            return os.path.exists(path)
        else:
            return self._remote_op(exists, path)

    def cd(self, path):
        # puts(green("cd '%s' on '%s'" % (path, self.host_string())))

        if self._is_local:
            return lcd(path)
        else:
            return cd(path)

    def create_project_folder(self):
        raise NotImplementedError('Subclass responsibility')

    def cd_project(self):
        return self.cd(self._project_path)

    def prefix(self, command):
        if self._is_local:
            raise RuntimeError("This a local machine, cannot use Fabric's 'prefix' command which is remote.")
        else:
            return prefix(command)

    def get(self, remote_path, local_path=None):
        if self._is_local:
            raise RuntimeError("This a local machine, cannot use Fabric's 'get' command which is remote.")
        else:
            return self._remote_op(get, remote_path=remote_path, local_path=local_path)

    # machine protocol - installs

    def install_postgresql_server(self, master_username, master_password):
        raise NotImplementedError('Subclass responsibility')

    def install_mysql_server(self):
        raise NotImplementedError('Subclass responsibility')

    # private

    def _run(self, command):
        if self._is_local:
            return local(command)
        else:
            return self._remote_op(run, command)

    def _remote_op(self, operation, *args, **kwargs):
        """
        Perform a remote operation using Fabric.
        This wraps network commands to ensure the correct host is used.

        Note: Context managers don't need to be wrapped.
        """

        env.host_string = self._ssh_connection
        result = operation(*args, **kwargs)
        env.host_string = None
        return result
