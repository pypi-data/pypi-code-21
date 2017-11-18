import os
import pip
import warnings
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
        for installed in pip.get_installed_distributions():
             if installed.project_name in self.required_projects:
                 self.required_projects[installed.project_name]['pkg'] = installed
        freeze_list = []
        for rp_name, value in self.required_projects.items():
            if not value.get("pkg"):
                warnings.warn("current python environment don't install required package: {}".format(rp_name), UserWarning)
            else:
                freeze_list.append("{}=={}".format(rp_name, value['pkg'].version))
        return freeze_list