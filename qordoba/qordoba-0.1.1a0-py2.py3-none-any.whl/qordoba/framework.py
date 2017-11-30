from __future__ import unicode_literals, print_function
from qordoba.utils import get_data
import os
import yaml
import re


class Framework(object):

    def __init__(self):

        self.strategy_name = 'framework'
        self.framework_strategies = {}
        framework_path = get_data('resources/framework.yml')
        with open(framework_path, 'r') as stream:
            try:
                self.framework_strategies = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def detect_paths_exists(self, dir_path, path_list):

        path_does_not_exist = False
        for path in path_list:
            if not os.path.exists(os.path.join(dir_path, path)):
                path_does_not_exist = True
                break

        return not path_does_not_exist

    def detect_regex_exists(self, dir_path, regex_configs):

        regex_failed = False
        for regex_config in regex_configs:

            if os.path.isfile(os.path.join(dir_path, regex_config['file'])):
                regex = re.compile(regex_config['search_term'])
                file = open(os.path.join(dir_path, regex_config['file']), 'r').read()
                match = regex.search(file)
                if not match:
                    regex_failed = True
                    break

        return not regex_failed

    def find_framework(self, dir_path):

        for framework in self.framework_strategies:
            path_list = self.framework_strategies[framework].get('paths', None)
            regex_list = self.framework_strategies[framework].get('regex', None)

            if path_list:
                paths_exists = self.detect_paths_exists(dir_path, path_list)
            else:
                paths_exists = True

            if regex_list:
                regex_exists = self.detect_regex_exists(dir_path, regex_list)
            else:
                regex_exists = True

            if paths_exists and regex_exists:
                return framework

        return "not found"
