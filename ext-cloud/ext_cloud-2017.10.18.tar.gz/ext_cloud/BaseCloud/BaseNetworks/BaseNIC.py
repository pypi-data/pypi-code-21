from abc import ABCMeta, abstractproperty


class BaseNICcls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return 'port'

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def state(self):
        pass
