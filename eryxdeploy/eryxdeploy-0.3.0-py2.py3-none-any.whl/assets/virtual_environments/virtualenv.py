from eryx_deploy.assets.virtual_environments.abs_virtual_environment import VirtualEnvironment


class Virtualenv(VirtualEnvironment):
    def first_time_setup(self):
        self._install_tool()
        self._create_env()

    def run(self, command, on_fail_msg=None):
        with self._host_machine.cd_project():
            with self._host_machine.prefix('source %s/bin/activate' % self._path):
                return self._host_machine.run(command, on_fail_msg=on_fail_msg)

    # private

    def _install_tool(self):
        self._host_machine.run('sudo -H pip install virtualenv')

    def _create_env(self):
        if not self._host_machine.path_exists(self._path):
            self._host_machine.run('virtualenv %s' % self._path)
