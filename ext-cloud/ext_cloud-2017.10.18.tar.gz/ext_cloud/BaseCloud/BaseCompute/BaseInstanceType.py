from abc import ABCMeta, abstractmethod, abstractproperty


class BaseInstanceTypecls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def memory(self):
        pass

    @abstractproperty
    def disk(self):
        pass

    @abstractmethod
    def cpus(self):
        pass
