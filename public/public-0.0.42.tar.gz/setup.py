#!/usr/bin/env python
# from distutils.core import setup # setuptools python3.2 not supported
from setuptools import setup
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

# ~/.pydistutils.cfg
# path/to/project.py/setup.cfg
# path/to/project.py/setup.py

def read_configuration(path):
    # setuptools.config.read_configuration read metadata/options ONLY
    result = dict()
    config = ConfigParser()
    config.read(path)
    for section in config.sections():
        for key, val in config.items(section):
            if "\n" in val:
                val = list(filter(None,val.splitlines()))
            if key == "description_file": # setuptools to distutils
                key = "long_description"
                val = open(val).read()
            result[key] = val
    return result

path = __file__.replace("setup.py","setup.cfg")
setup_cfg_data = read_configuration(path)
setup(**setup_cfg_data)


