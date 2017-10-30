from eryx_deploy.assets.package_managers.abs_package_manager import PackageManager


class FrontendPackageManager(PackageManager):
    """
    Frontend package manager

    For now, it only means it runs in a host machine.
    """

    def __init__(self, host_machine):
        self._host_machine = host_machine

    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility.')

    def update_dependencies(self):
        raise NotImplementedError('Subclass responsibility.')
