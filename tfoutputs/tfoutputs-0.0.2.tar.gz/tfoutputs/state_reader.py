import json


class StateReader(object):
    def __init__(self, file_paths):
        self.__file_paths = file_paths
        self.outputs = {}

    @property
    def file_paths(self):
        return self.__file_paths

    @file_paths.setter
    def file_paths(self, file_paths):
        self.__file_paths = file_paths

    def load_outputs(self):

        for file_path in self.__file_paths:
            with open(file_path, 'r') as f:
                json_file = json.load(f)
                for module in json_file['modules']:
                    self.parse_outputs(module)

    def parse_outputs(self, module):
        if module['path'] == ['root']:
            for key, value in module['outputs'].items():
                for output in self.outputs:
                    if key in output:
                        raise KeyError("Duplicate key found {0}".format(key))
                self.outputs[key] = value

    def __getattr__(self, item):
        try:
            if self.outputs[item]['sensitive']:
                return "sensitive value"
            else:
                return self.outputs[item]['value']
        except KeyError as e:
            print("ERROR: Either output: {0} does not exist in state reader or is an invalid attribute".format(item))
            raise
