#!/usr/bin/python

from xml.etree import ElementTree as ET


class ConfigParser:

    def __init__(self, config_file=""):
        self.config_file = config_file
        self.settings = {}

    def parse(self):
        return self.parse_file(self.config_file)

    def parse_file(self, config_file):
        self.__init__(config_file)

        settings_tree = ET.parse(config_file)
        settings_root = settings_tree.getroot()

        for setting_node in settings_root:
            self.settings[setting_node.attrib['key']] = setting_node.attrib['value']

        return self.settings
