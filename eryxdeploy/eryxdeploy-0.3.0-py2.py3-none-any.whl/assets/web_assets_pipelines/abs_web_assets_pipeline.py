class WebAssetsPipeline(object):
    def __init__(self, host_machine):
        self._host_machine = host_machine

    def first_time_setup(self):
        raise NotImplementedError('Subclass responsibility')

    def run_pipeline(self):
        raise NotImplementedError('Subclass responsibility')
