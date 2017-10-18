from abc import ABCMeta, abstractmethod, abstractproperty


class BaseNetworkcls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return 'network'

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def state(self):
        pass

    @abstractmethod
    def list_subnets(self):
        pass

    @abstractmethod
    def get_subnet_by_id(self, subnet_id):
        pass

    @abstractmethod
    def get_subnets_by_name(self, subnet_name):
        pass

    @abstractmethod
    def get_subnets_by_tag(self, tag_name, tag_value):
        pass

    @abstractmethod
    def create_subnet(self, name=None, cidr_block=None):
        pass
