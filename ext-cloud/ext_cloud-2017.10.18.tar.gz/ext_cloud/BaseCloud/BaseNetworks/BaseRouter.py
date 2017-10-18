from abc import ABCMeta, abstractproperty


class BaseRoutercls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return 'router'

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def state(self):
        pass
