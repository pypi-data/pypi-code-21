from abc import ABCMeta, abstractmethod


class CliHandlerInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cli_service(self, command_mode_type):
        pass
