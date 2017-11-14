# -*- coding: utf-8 -*-
# Author: lijian01
# Mail: lijian01@imdada.cn

import ConfigParser


class Configuration(object):
    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.config_parse = ConfigParser.RawConfigParser()
        self.all_conf = None
        self.setup()

    def setup(self):
        self.read_conf()

    def read_conf(self):
        self.config_parse.read(self.conf_path)

    def get_one_section_conf_dict(self, section_name):
        items_list = self.config_parse.items(section_name)

        return dict(items_list)

    def get_all_sections_dict(self):
        section_list = self.config_parse.sections()

        temp = list()
        for section in section_list:
            temp.append((section, self.get_one_section_conf_dict(section)))

        return dict(temp)

    @staticmethod
    def get_all_configurations(configure_file_path):
        cf = Configuration(configure_file_path)
        cf.read_conf()
        configs = cf.get_all_sections_dict()
        cf.all_conf = configs

        return cf

    def get_all_configurations_v2(self):
        self.all_conf = self.get_all_sections_dict()

        return self.all_conf

    def split_one_setting(self, section_name=None, item_name=None, sep=","):
        if section_name and item_name:
            temp_item = self.all_conf[section_name][item_name].strip()
            temp_item_list = temp_item.split(sep)
            item_list = [item.strip() for item in temp_item_list]

            return item_list


if __name__ == "__main__":
    uconfigure_file_path = "test_config.ini"
    cf_dict = Configuration.get_all_configurations(uconfigure_file_path)
    print cf_dict
