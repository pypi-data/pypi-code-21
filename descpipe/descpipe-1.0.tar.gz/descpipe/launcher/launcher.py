class Launcher:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.info = pipeline.cfg['runtime']

    # Not sure if these methods will be general to all 
    # translators?
    def config_dir(self):
        "Directory to search for pipeline configuration files"
        return self.info['config']

    def output_dir(self):
        "Directory to put results in at the end"
        return self.info['output']


