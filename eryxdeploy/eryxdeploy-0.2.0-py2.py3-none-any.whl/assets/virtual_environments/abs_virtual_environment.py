import os

from eryx_deploy.assets.abs_executable_environment import ExecutableEnvironment


class VirtualEnvironment(ExecutableEnvironment):
    def __init__(self, host_machine, name, path=None):
        self._host_machine = host_machine
        self._name = name

        if path:
            self._path = path
        else:
            self._path = os.path.join(self._host_machine.project_path(), self._name)

    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility.')

    def run(self, command, on_fail_msg=None):
        raise NotImplementedError('Subclass responsibility.')

    # TODO: Interesting stuff...
    # def __getattr__(self, name):
    #     return getattr(self._host_machine, name=name)
