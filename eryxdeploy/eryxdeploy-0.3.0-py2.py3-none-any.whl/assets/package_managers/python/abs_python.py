from eryx_deploy.assets.package_managers.abs_package_manager import PackageManager


class PythonPackageManager(PackageManager):
    """
    Python package manager
    """

    def __init__(self, virtual_environment, requirements_file_path):
        self._virtual_environment = virtual_environment
        self._requirements_file_path = requirements_file_path

    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility.')

    def update_dependencies(self):
        raise NotImplementedError('Subclass responsibility.')
