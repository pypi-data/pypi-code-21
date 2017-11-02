class FrameworkProject(object):
    def __init__(self, machine, project_name):
        self._host_machine = machine
        self._project_name = project_name

    def project_name(self):
        return self._project_name

    def first_time_setup(self):
        raise NotImplementedError("Subclass responsibility.")

    def after_pull_update(self):
        raise NotImplementedError("Subclass responsibility.")
