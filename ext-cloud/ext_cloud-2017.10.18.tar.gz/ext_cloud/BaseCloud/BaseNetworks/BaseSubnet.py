from abc import ABCMeta, abstractproperty


class BaseSubnetcls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return 'subnet'

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def state(self):
        pass
