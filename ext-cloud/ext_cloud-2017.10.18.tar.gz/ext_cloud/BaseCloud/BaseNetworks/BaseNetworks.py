from abc import ABCMeta, abstractmethod


class BaseNetworkscls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_networks(self):
        pass

    @abstractmethod
    def get_network_by_id(self, network_id):
        pass

    @abstractmethod
    def get_networks_by_name(self, network_name):
        pass

    @abstractmethod
    def get_networks_by_tag(self, tag_name, tag_value):
        pass

    @abstractmethod
    def create_network(self, name=None, cidr_block=None):
        pass
