from abc import ABCMeta, abstractproperty


class BaseServicecls:
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
    def status(self):
        pass

    @abstractproperty
    def port(self):
        pass

    @abstractproperty
    def host(self):
        pass
