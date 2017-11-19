import os
import pip
import warnings
from .core import freeze_version
try:
    from ConfigParser import ConfigParser
except:
    from configparser import ConfigParser
import re
from collections import OrderedDict


class Conf(object):
    def __init__(self):
        self.index = {}
        self.configs = {}

        self.get_config()

    def get_config(self):
        config_path = os.path.join(os.curdir, "requirements.ini")
        config = ConfigParser()
        with open(config_path) as fp:
            if hasattr(config, "read_file"):
                config.read_file(fp)
            else:
                config.readfp(fp)
        self.config = config
        self.required_projects = dict([(k, {'comment':v}) for k,v in self.config.items("requirements")])


    def get_freeze_requirements(self):
        return freeze_version(*self.required_projects.keys())

