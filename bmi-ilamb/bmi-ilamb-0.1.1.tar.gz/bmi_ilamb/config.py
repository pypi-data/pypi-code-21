"""Reads and parses a configuration file for the ILAMB BMI."""

from os.path import join
import yaml


ilamb_root_key = 'ilamb_root'
model_root_key = 'model_root'
models_key = 'models'
confrontations_key = 'confrontations'


class Configuration(object):

    def __init__(self, filename=None):
        self._config = {}
        if filename is not None:
            self.load(filename)

    def load(self, filename):
        with open(filename, 'r') as fp:
            self._config = yaml.load(fp)

    def get_ilamb_root(self):
        return self._config.get(ilamb_root_key)

    def _set_model_root(self):
        rel = self._config.get(model_root_key)
        if rel is not None:
            self._config[model_root_key] = join(self.get_ilamb_root(), rel)

    def get_arguments(self):
        args = []
        self._set_model_root()
        for k, v in self._config.iteritems():
            if (k != ilamb_root_key) and (v is not None) and (len(v) > 0):
                args.append('--' + k)
                args.extend([v] if type(v) == str else v)
        return args
