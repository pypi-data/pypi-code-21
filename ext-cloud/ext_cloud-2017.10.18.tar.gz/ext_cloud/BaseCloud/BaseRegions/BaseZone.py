from abc import ABCMeta, abstractproperty


class BaseZonecls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def state(self):
        pass

    @abstractproperty
    def hosts_count(self):
        pass
