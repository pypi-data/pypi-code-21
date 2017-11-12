from abc import ABCMeta
from abc import abstractmethod


class RunCommandInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def run_custom_command(self, command):
        pass

    @abstractmethod
    def run_custom_config_command(self, command):
        pass
