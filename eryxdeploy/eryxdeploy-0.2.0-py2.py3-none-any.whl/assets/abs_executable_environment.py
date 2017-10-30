class ExecutableEnvironment(object):
    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility.')

    def run(self, command, on_fail_msg=None):
        raise NotImplementedError('Subclass responsibility.')
