import importlib
import os


class StateConfigurator(object):
    def __init__(self, config):
        self.__config = config
        self.__state_files = []

    @property
    def config(self):
        return self.__config

    @property
    def state_files(self):
        return self.__state_files

    @state_files.setter
    def state_files(self, file_paths):
        if isinstance(file_paths, list):
            self.__state_files.extend(file_paths)
        if isinstance(file_paths, str):
            self.__state_files.append(file_paths)
        else:
            raise TypeError(
                "invalid type for state file setter {0} - should be string or list".format(type(file_paths)))

    @config.setter
    def config(self, config):
        if isinstance(config, dict):
            self.__config = [config]
        elif isinstance(config, list):
            self.__config = config
        else:
            raise TypeError("expected either a dict or list but got {0}".format(type(config)))

    def files_from_backend(self):
        for item in self.config:
            backend = item['backend']
            backend_instance = StateConfigurator.backend_for(backend)
            self.state_files = backend_instance(item['options']).save()

    @staticmethod
    def backend_for(backend):
        backend_class = "{0}Backend".format(backend.capitalize())
        try:
            backend_module = importlib.import_module("tfoutputs.backend")
            class_name = (getattr(backend_module, backend_class))
            return class_name
        except AttributeError:
            print("Failed to load backend {0}".format(backend))
            raise
        except ModuleNotFoundError:
            print("Failed to load backend {0}".format(backend))
            raise

    def cleanup(self):
        for file in self.__state_files:
            os.unlink(file)

