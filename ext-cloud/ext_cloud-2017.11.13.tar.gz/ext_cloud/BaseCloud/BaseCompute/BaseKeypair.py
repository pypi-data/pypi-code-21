from abc import ABCMeta, abstractmethod, abstractproperty


class BaseKeypaircls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def privatekey(self):
        pass

    @abstractproperty
    def publickey(self):
        pass

    @abstractmethod
    def delete(self):
        pass
