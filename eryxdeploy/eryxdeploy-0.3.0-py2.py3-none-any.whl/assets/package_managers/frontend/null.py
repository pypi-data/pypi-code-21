from eryx_deploy.assets.package_managers.frontend.abs_frontend import FrontendPackageManager


class NullPackageManager(FrontendPackageManager):
    def first_time_setup(self):
        pass  # do nothing

    def update_dependencies(self):
        pass  # do nothing
