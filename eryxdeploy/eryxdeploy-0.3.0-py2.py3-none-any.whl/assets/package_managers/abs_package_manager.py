class PackageManager(object):
    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility.')

    def update_dependencies(self):
        raise NotImplementedError('Subclass responsibility.')
