from abc import ABCMeta, abstractmethod


class BaseServicescls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_services(self):
        pass

    @abstractmethod
    def list_network_services(self):
        pass

    @abstractmethod
    def list_compute_services(self):
        pass
