
import yaml


class Config(dict):

    def __init__(self, file=None, config=None, **kwargs):
        config = config or {}

        if file:
            config = self._load_config(file)

        if kwargs:
            config.update(kwargs)

        self.update(config)

    def _load_config(self, file):
        with open(file, "r") as fd:
            return yaml.load(fd.read())

load_config = Config
