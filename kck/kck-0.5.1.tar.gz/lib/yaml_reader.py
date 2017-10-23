import yaml

from .err import handle_error

class YAMLReader(object):
    @staticmethod
    def read_yaml(filepath, on_error=None):
        """read/parse a yaml file, return resulting object"""
        with open(filepath, 'r') as stream:
            try:
                ret = yaml.load(stream)
                return ret
            except yaml.YAMLError as exc:
                handle_error(exc, "unable to read yaml file: {}".format(filepath), on_error)