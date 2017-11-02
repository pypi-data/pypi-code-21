from eryx_deploy.assets.package_managers.frontend.abs_frontend import FrontendPackageManager


class NPM(FrontendPackageManager):
    def first_time_setup(self):
        self._host_machine.install_nodejs()

    def update_dependencies(self):
        with self._host_machine.cd_project():
            self._host_machine.run("npm install")
