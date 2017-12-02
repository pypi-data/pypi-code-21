##
# @file configfile.py
# @brief Parse for the YAML config files.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03


import yaml


class YAMLConfigFile(object):
    def __init__(self, filename):
        with open(filename, "r") as yamlfile:
            self._data = yaml.load(yamlfile.read())

    def getData(self):
        return self._data.copy()
